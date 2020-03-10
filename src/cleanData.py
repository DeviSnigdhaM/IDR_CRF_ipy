import pandas as pd
import os
import json

IXSet = "../datasets/Annotations"
cleanOCRSet = "../datasets/CleanOCR"
nerDataset = "../datasets/ner-dataset.csv"

def dataAnnotation():
	allCleanOCRFiles = os.listdir(cleanOCRSet)
	allIXFiles = os.listdir(IXSet)
	outfile = open(nerDataset, 'w')
	receiptNum = 1
	outfile.write('Receipt #,Word,POS,Tag' + '\n')

	for ixfile in allIXFiles:
		filename = os.fsdecode(ixfile)
		for ocrfile in allCleanOCRFiles:
			ocrFilename = os.fsdecode(ocrfile)
			if filename == ocrFilename:
				ixData = {}
				ocrCleanLine = ""
				print ("Processing file: ", filename)
				with open(IXSet + '/' + filename) as f1:
					ixData = json.load(f1)
				with open(cleanOCRSet + '/' + filename) as f2:
					ocrCleanLine = f2.readlines()
				annotationLine = ""
				wordNum = 0
				words = ocrCleanLine[0].replace(',', '').split(' ')
				isAmount = False
				isDate = False
				isMerchant = False
				beginMerchant = False
				beginDate = False

				merchantParts = ixData['company'].split(' ')
				dateParts = ixData['date'].split(' ')
				
				for word in words:
					annotationLine = ""
					word = word.replace(',', ' ')
					if wordNum == 0:
						if word == dateParts[0] and not isDate:
							annotationLine = 'Receipt: ' + str(receiptNum) + ',' + word + ',' + "DT" + ',' + 'B-date'
							isDate = True
							# Only expect a I-date if there are multiple parts to the date
							if len(dateParts) > 1:
								beginDate = True
							else:
								beginDate = False
						elif word == ixData['total'] and not isAmount:
							annotationLine = 'Receipt: ' + str(receiptNum) + ',' + word + ',' + "AM" + ',' + 'B-amt'
							isAmount = True
						elif word == merchantParts[0] and not isMerchant:
							annotationLine = 'Receipt: ' + str(receiptNum) + ',' + word + ',' + "MR" + ',' + 'B-mer'
							isMerchant = True
							beginMerchant = True
						else:
							annotationLine = 'Receipt: ' + str(receiptNum) + ',' + word + ',' + "NN" + ',' + 'O'
					else:
						#Date tagging
						if word == dateParts[0] and not isDate:
							annotationLine = ',' + word + ',' + "DT" + ',' + 'B-date'
							isDate = True
							# Only expect a I-date if there are multiple parts to the date
							if len(dateParts) > 1:
								# print("This date has many parts: " + ixData['date'])
								beginDate = True
							else:
								beginDate = False
						elif word in ixData['date'] and word != dateParts[0] and word != dateParts[-1] and beginDate:
							annotationLine = ',' + word + ',' + "DT" + ',' + 'I-date'
						elif word == dateParts[-1] and beginDate:
							beginDate = False
							annotationLine = ',' + word + ',' + "DT" + ',' + 'I-date'

						#Amount tagging
						elif word == ixData['total'] and not isAmount:
							annotationLine = ',' + word + ',' + "AM" + ',' + 'B-amt'
							isAmount = True

						#Merchant tagging
						elif word == merchantParts[0] and not isMerchant:
							beginMerchant = True
							isMerchant = True
							annotationLine = ',' + word + ',' + "MR" + ',' + 'B-mer'
						elif word in ixData['company'] and word != merchantParts[0] and word != merchantParts[-1] and beginMerchant:
							annotationLine = ',' + word + ',' + "MR" + ',' + 'I-mer'
						elif word == merchantParts[-1] and beginMerchant:
							beginMerchant = False
							annotationLine = ',' + word + ',' + "MR" + ',' + 'I-mer'

						#Other tagging
						else:
							annotationLine = ',' + word + ',' + "NN" + ',' + 'O'
					wordNum += 1						
					#print(annotationLine)
					outfile.write(annotationLine + '\n')
				receiptNum += 1
	outfile.close

def main():
	#cleanOCRFiles()
	dataAnnotation()

main()