import openpyxl
from datetime import datetime
import csv
import os

class ImportWorksheet:

    def __init__(self, varPath, varID, workDir):
        self.varPath = varPath
        self.varID = varID
        self.workDir = workDir
        self.timeNow = datetime.now().strftime("%Y-%m-%d %H%M")
        self.newWbName = f"{self.workDir}{self.varID} regex {self.timeNow}.xlsx"
        self.wb = self.createCopy()
        self.ws_main = self.wb.get_sheet_by_name("STARLiMS_import")
        self.ws_main_noRows = self.ws_main.max_row
        self.createWorksheets()

    def createCopy(self):
        openpyxl.load_workbook(self.varPath).save(self.newWbName)
        return openpyxl.load_workbook(self.newWbName)

    def createWorksheets(self):
        # Create new sheet and populate header for mutation surveyor import file
        ws_ms = self.wb.create_sheet("MutationSurveyor")
        header_ms = ["Sample Name", "Reference Name", "Lane Quality", "ROI Coverage", "#nts below threshold",
                    "Quality ROI", "Variant1", "Variant2", "Variant3", "Variant4"]
        ws_ms.cell(row=1, column=1).value = "Warning!"
        for i in range(len(header_ms)):
            ws_ms.cell(row=2, column=i+1).value = header_ms[i]

        # Create new sheet and populate header for variant details import file
        ws_var = self.wb.create_sheet("VariantDetails")
        header_var = ["Well", "Sample", "VariantDetails",
                      "Gene1", "Zygosity1", "Inheritance1", "HGVS1", "Genomic1", "Pathogenicity1",
                      "Gene2", "Zygosity2", "Inheritance2", "HGVS2", "Genomic2", "Pathogenicity2",
                      "Gene3", "Zygosity3", "Inheritance3", "HGVS3", "Genomic3", "Pathogenicity3"]
        for i in range(len(header_var)):
            ws_var.cell(row=1, column=i+1).value = header_var[i]
        self.wb.save(self.newWbName)

    def single_amino_code(aa3):
        aa_dict = {'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D', 'Cys': 'C',
                   'Glu': 'E', 'Gln': 'Q', 'Gly': 'G', 'His': 'H', 'Ile': 'I', 'Leu': 'L',
                   'Lys': 'K', 'Met': 'M', 'Phe': 'F', 'Pro': 'P', 'Ser': 'S', 'Thr': 'T',
                   'Trp': 'W', 'Tyr': 'Y', 'Val': 'V', 'Ter': 'X', '?': '?'}
        return aa_dict[aa3]

    def write_variantDetails(self, sample_var):
        ws_var = self.wb.get_sheet_by_name("VariantDetails")
        for i, sample in enumerate(sample_var):
            ws_var.cell(row=i+2, column=1).value = sample_var[sample][0]
            ws_var.cell(row=i+2, column=2).value = sample

            variant = ""
            col_count = 4
            for x in range(2, len(sample_var[sample])):
                sampleInfo = sample_var[sample][x]
                if sampleInfo.variantPresent is True and sampleInfo.confirmationRqd is False:
                    variant += f"{sampleInfo.gene} {sampleInfo.genotype[:3]} " \
                               f"p.{sampleInfo.pNom} c.{sampleInfo.cNom['cFull']}; "
                    ws_var.cell(row=i + 2, column=col_count).value = sampleInfo.gene
                    ws_var.cell(row=i + 2, column=col_count + 1).value = sampleInfo.genotype
                    ws_var.cell(row=i + 2, column=col_count + 2).value = "Maternal/Paternal/Biparental/De novo"
                    ws_var.cell(row=i + 2, column=col_count + 3).value = \
                        f"{sampleInfo.transcript}:c.{sampleInfo.cNom['cFull']}, p.{sampleInfo.pNom}"
                    ws_var.cell(row=i + 2, column=col_count + 4).value = \
                        f"Chr{sampleInfo.chr}(GRCh37):g.{sampleInfo.gNom['gFull']}"
                    ws_var.cell(row=i + 2, column=col_count + 5).value = sampleInfo.variantStatus
                    col_count += 6
                elif sampleInfo.variantPresent is True and sampleInfo.confirmationRqd is True:
                    variant += f"{sampleInfo.gene} confirmation/in-fill; "

            ws_var.cell(row=i+2, column=3).value = variant
        self.wb.save(self.newWbName)
        self.to_csv("VariantDetails")


    def write_mutationSurveyor(self, sample_var):
        ws_ms = self.wb.get_sheet_by_name("MutationSurveyor")
        for i, sample in enumerate(sample_var):
            ws_ms.cell(row=3+i, column=1).value = sample_var[sample][1]

            # for x in range(2, len(sample_var[sample])):
            #     sampleInfo = sample_var[sample][x]
            #     if sampleInfo.variantPresent is True and sampleInfo.confirmationRqd is False:

        self.wb.save(self.newWbName)

    def mutationSurveyorFormat(self, variant):
        if variant.genotype == "Heterozygous":
            if variant.codingEffect == "Synonymous":
                return f"c.[{variant.cNom['cFull']}]+[=],"
        elif variant.genotype == "Homozygous":
            pass

    def to_csv(self, sheet):
        ws = self.wb.get_sheet_by_name(sheet)
        with open(f"{self.workDir}{self.varID} {sheet} {self.timeNow}.csv", 'w', newline='') as f:
            c = csv.writer(f)
            for r in ws.rows:
                c.writerow([cell.value for cell in r])

    def closeWs(self):
        self.wb.close()






