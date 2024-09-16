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

	# Create output directory
	out_dir = os.path.join("output", f"out_{int(time.time())}")
	os.makedirs(out_dir)
	# Create sql file
	out_file = open(f"{os.path.join(out_dir, "insert.sql")}", "w")
	# Create uploads directory
	out_uploads = os.path.join(out_dir, "uploads")
	os.makedirs(out_uploads)

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

	# Ensure all columns are strings
	print("Converting columns to strings")
	for col in df.columns:
		df[col] = df[col].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))

	# Create types
	print("Generating types")
	for t in df.Type.unique():
		out_file.write(nanoorm.insert("types", type=t) + "\n")

	# Create tags
	print("Generating tags")
	df_composer = df.Composer.dropna().str.strip().str.split('/').explode().unique().tolist()
	df_instrument = df.Instrument.dropna().str.strip().str.split('/').explode().unique().tolist()
	df_grade = df.Grade.dropna().unique().tolist()
	df_scale = df.Scale.dropna().str.strip().str.split('/').explode().unique().tolist()
	tags = df_composer + df_instrument + df_grade + df_scale
	for t in tags:
		out_file.write(nanoorm.insert("tags", type=t) + "\n")

	# Create pieces
	print("Generating pieces")
	df_piece = df.Name.dropna().unique().tolist()
	for p in df_piece:
		out_file.write(nanoorm.insert("pieces", name=p) + "\n")

	# Bind pieces and tags
	print("Binding pieces and tags")
	df_tags = df
	df_tags['Composer'] = df_tags['Composer'].str.split('/')
	df_tags['Instrument'] = df_tags['Instrument'].str.split('/')
	df_tags['Grade'] = df_tags['Grade'].str.split('/')
	df_tags['Scale'] = df_tags['Scale'].str.split('/')
	df_tags = df_tags.groupby("Name").agg({
		'Composer': lambda x: [item for sublist in x for item in sublist],
		'Instrument': lambda x: [item for sublist in x for item in sublist],
		'Grade': lambda x: [item for sublist in x for item in sublist],
		'Scale': lambda x: [item for sublist in x for item in sublist]
	}).reset_index()
	for index, row in df_tags.iterrows():
		row_tags = list(set(row.Composer + row.Instrument + row.Grade + row.Scale))
		for tag in row_tags:
			out_file.write(f"INSERT INTO piece_tag (piece_id, tag_id) VALUES ((SELECT id FROM pieces WHERE name = '{row.Name}'), (SELECT id FROM tags WHERE name = '{tag}'));\n")

	# Create items
	print("Generating items")
	for index, row in df.iterrows():
		# Process files
		pass


if __name__ == '__main__':
	main()
