Instructions to launch:
	To use the parser put tomitaparser.exe in news_parser/tomita

	python news_parser.py [-d] [-i <input_file>] [-o <output_file>] [-p <float>]

	-d - Enable debug output to debug.txt, default = False
	-i - Relative input file path, default = "output.csv"
		NOTE: FILE MUST BE ENCODED WITH UTF-8
	-o - Relative output file path, default = "output.csv"
	-e - Enable fuzzy name matching, inputting anything except "true" and "1" will evaluate to "False", default = False
		NOTE: SLOWS DOWN THE PROCESS UP TO 3 TIMES, USE WITH TINY FILES ONLY
	-p - Fuzzy match threshold between 0.5 and 1, only effective with "-e 1", default = 0.65.