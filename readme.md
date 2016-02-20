Instructions to launch:
	To use the parser put tomitaparser.exe in news_parser/tomita

	python news_parser.py [-d] [-i <input_file>] [-o <output_file>] [-p <float>]

	-d - Enable debug output to debug.txt, default = False
	-i - Relative input file path, default = "output.csv"
	-o - Relative output file path, default = "output.csv"
	-p - Fuzzy match threshold between 0.5 and 1, default = 0.65.