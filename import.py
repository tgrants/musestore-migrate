import json
import nanoorm
import os
import pandas as pd
import sqlite3
import time

from argparse import ArgumentParser, RawDescriptionHelpFormatter

module_version = "0.1"


def main():
	parser = ArgumentParser(
		formatter_class = RawDescriptionHelpFormatter
	)
	parser.add_argument(
		"--version",
		action = "version",
		version = module_version,
		help = "Display version information and dependencies.",
	)
	parser.add_argument(
		"file",
		help = "Path to input file."
	)
	args = parser.parse_args()

	df = pd.read_csv(args.file)

	fout = open(f"{os.path.join("output", f"out_{int(time.time())}.sql")}", "w") # output file

	# Rename the columns to english
	print("Checking column names")
	with open('lang.json', 'r') as lang_file:
		lang_data = json.load(lang_file)
	rename_dict = {}
	# Iterate through each column in the DataFrame
	for column in df.columns:
		# Iterate through each key in the JSON data
		for key, translations in lang_data.items():
			# Check if the column name matches any translation in any language
			if any(column == lang[lang_code] for lang in translations for lang_code in lang):
				# If a match is found, map it to the English equivalent
				rename_dict[column] = translations[0]['en']
				break  # Stop searching after the first match
	# Rename the DataFrame columns using the mapping dictionary
	df.rename(columns=rename_dict, inplace=True)

	# Drop duplicate IDs
	print("Dropping duplicate IDs")
	df = df.drop_duplicates(subset='ID', keep='first')

	# Create types
	print("Generating types")
	for t in df.Type.unique():
		fout.write(nanoorm.insert("types", type=t) + "\n")

	# Create tags
	print("Generating tags")
	df_composer = df.Composer.dropna().str.strip().str.split('/').explode().unique().tolist()
	df_instrument = df.Instrument.dropna().str.strip().str.split('/').explode().unique().tolist()
	df_grade = df.Grade.dropna().unique().tolist()
	df_scale = df.Scale.dropna().str.strip().str.split('/').explode().unique().tolist()
	tags = df_composer + df_instrument + df_grade + df_scale
	for t in tags:
		fout.write(nanoorm.insert("tags", type=t) + "\n")

	# Create pieces and items
	print("Generating pieces and items")
	pass


if __name__ == '__main__':
	main()
