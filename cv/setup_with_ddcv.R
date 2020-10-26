library(datadrivencv)
library(here)
use_datadriven_cv(
  full_name = "Seonggyu Park",
  data_location = "https://docs.google.com/spreadsheets/d/1VIk_ov2KU34-eayiOAJqeci-3m3tumNiVMqlCfIKCjM/edit?usp=sharing",
  pdf_location = "https://github.com/spark-brc/CVs/raw/master/spark_cv.pdf",
  html_location = "https://spark-brc.github.io/cv/",
  source_location = "https://github.com/spark-brc/CVs",
  output_dir = here(),
  open_files = FALSE
)
