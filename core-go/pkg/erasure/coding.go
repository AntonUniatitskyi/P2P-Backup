package erasure

import (
	"io"

	"github.com/klauspost/reedsolomon"
)

// Encoder оборачивает библиотеку Рида-Соломона
type Encoder struct {
	dataShards   int
	parityShards int
	rs           reedsolomon.Encoder
}

func NewEncoder(data, parity int) (*Encoder, error) {
	enc, err := reedsolomon.New(data, parity)
	if err != nil {
		return nil, err
	}
	return &Encoder{dataShards: data, parityShards: parity, rs: enc}, nil
}

func (e *Encoder) EncodeData(data []byte) ([][]byte, error) {
	shards, err := e.rs.Split(data)
	if err != nil {
		return nil, err
	}
	err = e.rs.Encode(shards)
	return shards, err
}

func (e *Encoder) ReconstructData(shards [][]byte) error {
	return e.rs.Reconstruct(shards)
}

// JoinData склеивает шарды обратно в исходный файл, обрезая паддинг
// по оригинальному размеру (без этого в конец файла попадут лишние нулевые байты).
func (e *Encoder) JoinData(dst io.Writer, shards [][]byte, originalSize int64) error {
	return e.rs.Join(dst, shards, int(originalSize))
}
