# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os
import logging

from util import list_all_files
from spc_ex import spc_ex
from rsct_ex import rsct_ex
from srd_ex import srd_ex
from stx_ex import stx_ex
from wrd_ex import wrd_ex
from logutil import setup_logging, get_logger

OUT_DIR = "dec"
LOG_FILE_NAME = "drv3_ex_all.log"

def safe_run(logger, counters, step, filename, fn, *args, **kwargs):
  counters["total"] += 1
  
  try:
    fn(*args, **kwargs)
    counters["succeeded"] += 1
    return True
  
  except Exception:
    counters["failed"] += 1
    logger.exception("%s failed: %s", step, filename)
    return False

if __name__ == "__main__":
  import argparse
  
  parser = argparse.ArgumentParser(description = "Extracts data used in New Danganronpa V3.")
  parser.add_argument("input", metavar = "<input dir>", nargs = "+", help = "An input directory.")
  parser.add_argument("-o", "--output", metavar = "<output dir>", help = "The output directory.")
  parser.add_argument("--log-file", metavar = "<log file>", help = "Override log file path.")
  parser.add_argument("--verbose", action = "store_true", help = "Show INFO logs in the console.")
  parser.add_argument("--no-crop", dest = "crop", action = "store_false", help = "Don't crop srd textures to their display dimensions.")
  args = parser.parse_args()
  
  console_level = logging.INFO if args.verbose else logging.ERROR
  grand_total = {"total": 0, "succeeded": 0, "failed": 0}
  
  for in_path in args.input:
    
    if os.path.isdir(in_path):
      base_dir = os.path.normpath(in_path)
      files = list_all_files(base_dir) or []
    else:
      continue
    
    if args.output:
      out_dir = os.path.normpath(args.output)
      out_dir = os.path.join(out_dir, os.path.basename(base_dir))
    else:
      split = os.path.split(base_dir)
      out_dir = os.path.join(split[0], OUT_DIR, split[1])
    
    log_file = args.log_file or os.path.join(out_dir, LOG_FILE_NAME)
    logger = setup_logging(log_file, console_level = console_level, file_level = logging.ERROR)
    counters = {"total": 0, "succeeded": 0, "failed": 0}
    
    logger.info("*****************************************************************")
    logger.info("* New Danganronpa V3 extractor, written by BlackDragonHunt.      ")
    logger.info("*****************************************************************")
    logger.info("Input directory: %s", base_dir)
    logger.info("Output directory: %s", out_dir)
    logger.info("Log file: %s", log_file)
  
    if out_dir == base_dir:
      logger.error("Input and output directories are the same: %s", out_dir)
      logger.error("Continuing will cause the original data to be overwritten.")
      s = input("Continue? y/n: ")
      if not s[:1].lower() == "y":
        continue
    
    # Extract the SPC files.
    for filename in files:
      out_file = os.path.join(out_dir, filename[len(base_dir) + 1:])
      
      if not os.path.splitext(filename)[1].lower() == ".spc":
        continue
      
      logger.info("Extracting SPC: %s", filename)
      safe_run(logger, counters, "SPC extract", filename, spc_ex, filename, out_file)
    
    # Now extract all the data we know how to from inside the SPC files.
    for filename in list_all_files(out_dir) or []:
      ext = os.path.splitext(filename)[1].lower()
      
      if not ext in [".rsct", ".wrd", ".stx", ".srd"]:
        continue
      
      ex_dir, basename = os.path.split(filename)
      ex_dir   = out_dir + "-ex" + ex_dir[len(out_dir):]
      txt_file = os.path.join(ex_dir, os.path.splitext(basename)[0] + ".txt")
      
      logger.info("Extracting data: %s", filename)
      
      if ext == ".rsct":
        safe_run(logger, counters, "RSCT extract", filename, rsct_ex, filename, txt_file)
      
      if ext == ".wrd":
        safe_run(logger, counters, "WRD extract", filename, wrd_ex, filename, txt_file)
      
      if ext == ".stx":
        safe_run(logger, counters, "STX extract", filename, stx_ex, filename, txt_file)
      
      # Because we have the same extensions used for multiple different formats.
      if ext == ".srd" or ext == ".stx":
        safe_run(logger, counters, "SRD extract", filename, srd_ex, filename, ex_dir, crop = args.crop)
    
    summary_msg = "Summary for %s | total=%d success=%d failed=%d"
    summary_args = (base_dir, counters["total"], counters["succeeded"], counters["failed"])
    if counters["failed"] > 0:
      logger.error(summary_msg, *summary_args)
    else:
      logger.info(summary_msg, *summary_args)
    grand_total["total"] += counters["total"]
    grand_total["succeeded"] += counters["succeeded"]
    grand_total["failed"] += counters["failed"]
  
  final_logger = get_logger(__name__)
  if grand_total["failed"] > 0:
    final_logger.error("Overall summary | total=%d success=%d failed=%d",
                      grand_total["total"], grand_total["succeeded"], grand_total["failed"])
  else:
    final_logger.info("Overall summary | total=%d success=%d failed=%d",
                      grand_total["total"], grand_total["succeeded"], grand_total["failed"])
  input("Press Enter to exit.")

### EOF ###
