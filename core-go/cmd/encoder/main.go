package main

import (
	"flag"
	"fmt"
	"os"
	"p2p-backup/pkg/erasure"
	"p2p-backup/pkg/storage"
	"path/filepath"
	"strings"
)

func main() {
	mode := flag.String("mode", "split", "Режим: split или join")
	filePath := flag.String("file", "", "Путь к исходному файлу (только split)")
	outPath := flag.String("out", "", "Путь для записи восстановленного файла (только join)")
	baseNameFlag := flag.String("basename", "", "Имя файла для поиска шардов (только join)")
	dataShards := flag.Int("data", 3, "Количество блоков данных (K)")
	parityShards := flag.Int("parity", 2, "Количество блоков паритета (M)")
	dirsStr := flag.String("dirs", "", "Список целевых папок через запятую")
	flag.Parse()

	if *dirsStr == "" {
		fmt.Println("Ошибка: Укажите -dirs")
		os.Exit(1)
	}
	targetDirs := strings.Split(*dirsStr, ",")

	if *mode == "split" {
		if *filePath == "" {
			fmt.Println("Ошибка: Укажите -file")
			os.Exit(1)
		}

		enc, err := erasure.NewEncoder(*dataShards, *parityShards)
		if err != nil {
			fmt.Printf("Ошибка кодировщика: %v\n", err)
			os.Exit(1)
		}

		data, err := os.ReadFile(*filePath)
		if err != nil {
			fmt.Printf("Ошибка чтения файла: %v\n", err)
			os.Exit(1)
		}

		shards, err := enc.EncodeData(data)
		if err != nil {
			fmt.Printf("Ошибка кодирования: %v\n", err)
			os.Exit(1)
		}

		baseName := filepath.Base(*filePath)
		err = storage.SaveShards(baseName, shards, targetDirs, int64(len(data)), *dataShards, *parityShards)
		if err != nil {
			fmt.Printf("Ошибка сохранения: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("[Go Core] Файл успешно разбит и распределен по выбранным путям!")

	} else if *mode == "join" {
		if *baseNameFlag == "" || *outPath == "" {
			fmt.Println("Ошибка: Укажите -basename и -out")
			os.Exit(1)
		}

		fmt.Println("[Go Core] Поиск манифеста...")
		manifest, err := storage.LoadManifest(*baseNameFlag, targetDirs)
		if err != nil {
			fmt.Printf("[Ошибка]: %v\n", err)
			os.Exit(1)
		}

		fmt.Println("[Go Core] Поиск и чтение доступных чанков...")
		shards, err := storage.LoadShards(*baseNameFlag, manifest.DataShards+manifest.ParityShards, targetDirs)
		if err != nil {
			fmt.Printf("Ошибка загрузки чанков: %v\n", err)
			os.Exit(1)
		}

		enc, err := erasure.NewEncoder(manifest.DataShards, manifest.ParityShards)
		if err != nil {
			fmt.Printf("Ошибка кодировщика: %v\n", err)
			os.Exit(1)
		}

		fmt.Println("[Go Core] Запуск математической регенерации данных...")
		err = enc.ReconstructData(shards)
		if err != nil {
			fmt.Printf("[Критическая ошибка]: Невозможно восстановить! Потеряно слишком много флешек: %v\n", err)
			os.Exit(1)
		}

		outFile, err := os.Create(*outPath)
		if err != nil {
			fmt.Printf("Ошибка создания файла для восстановления: %v\n", err)
			os.Exit(1)
		}
		defer outFile.Close()

		err = enc.JoinData(outFile, shards, manifest.OriginalSize)
		if err != nil {
			fmt.Printf("Ошибка записи восстановленного файла: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("[Go Core] Восстановление завершено! Файл собран в: %s\n", *outPath)
	}
}
