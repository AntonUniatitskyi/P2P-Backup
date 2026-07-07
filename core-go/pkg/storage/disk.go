package storage

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Manifest хранит метаданные, необходимые для точного восстановления файла
type Manifest struct {
	OriginalName string `json:"original_name"`
	OriginalSize int64  `json:"original_size"`
	DataShards   int    `json:"data_shards"`
	ParityShards int    `json:"parity_shards"`
}

// SaveShards раскладывает чанки по указанным путям (папкам флешек)
// и кладёт рядом манифест с оригинальным размером и параметрами K/M.
func SaveShards(baseName string, shards [][]byte, targetDirs []string, originalSize int64, dataShards, parityShards int) error {
	for i, shard := range shards {
		dir := targetDirs[i%len(targetDirs)]
		_ = os.MkdirAll(dir, 0755)

		shardName := fmt.Sprintf("%s.shard.%d", baseName, i)
		err := os.WriteFile(filepath.Join(dir, shardName), shard, 0644)
		if err != nil {
			return fmt.Errorf("ошибка записи чанка %d в %s: %w", i, dir, err)
		}
	}

	manifest := Manifest{
		OriginalName: baseName,
		OriginalSize: originalSize,
		DataShards:   dataShards,
		ParityShards: parityShards,
	}
	manifestBytes, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return fmt.Errorf("ошибка сериализации манифеста: %w", err)
	}

	// Манифест кладём во все папки — на случай, если часть флешек отвалится
	manifestName := fmt.Sprintf("%s.meta", baseName)
	for _, dir := range targetDirs {
		_ = os.WriteFile(filepath.Join(dir, manifestName), manifestBytes, 0644)
	}

	return nil
}

// LoadManifest ищет манифест в доступных директориях
func LoadManifest(baseName string, sourceDirs []string) (*Manifest, error) {
	manifestName := fmt.Sprintf("%s.meta", baseName)

	for _, dir := range sourceDirs {
		data, err := os.ReadFile(filepath.Join(dir, manifestName))
		if err == nil {
			var m Manifest
			if err := json.Unmarshal(data, &m); err != nil {
				continue
			}
			return &m, nil
		}
	}
	return nil, fmt.Errorf("манифест %s не найден ни в одной из указанных папок", manifestName)
}

// LoadShards пытается прочитать чанки из известных мест
func LoadShards(baseName string, totalShards int, sourceDirs []string) ([][]byte, error) {
	shards := make([][]byte, totalShards)

	for i := 0; i < totalShards; i++ {
		shardName := fmt.Sprintf("%s.shard.%d", baseName, i)
		var shardData []byte
		var found bool

		for _, dir := range sourceDirs {
			data, err := os.ReadFile(filepath.Join(dir, shardName))
			if err == nil {
				shardData = data
				found = true
				break
			}
		}

		if found {
			shards[i] = shardData
		} else {
			shards[i] = nil // Чанк потерян (диск отключен)
		}
	}
	return shards, nil
}
