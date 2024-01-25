#!/bin/bash

if [ $1 == "RDAC" ]; then 
python $1_$2.py  --original_seq $3 --encoding_frames $4 --quantization_factor $5 --Iframe_QP $6 --Iframe_format $7 --adaptive_metric $8 --adaptive_thresh $9 --rate_idx ${10} --int_value ${11} --gop_size ${12}
elif [ $1 == "DAC" ]; then
python $1_$2.py  --original_seq $3 --encoding_frames $4 --quantization_factor $5 --Iframe_QP $6 --Iframe_format $7 --adaptive_metric $8 --adaptive_thresh $9
else
python $1_$2.py  --original_seq $3 --encoding_frames $4 --quantization_factor $5 --Iframe_QP $6 --Iframe_format $7
fi