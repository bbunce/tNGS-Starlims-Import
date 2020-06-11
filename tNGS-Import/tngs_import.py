import pandas as pd
import os
from datetime import datetime

class Import():

    def __init__(self, regexFile, seqLoadFile):
        self.regexFile = regexFile
        self.seqLoadFile = seqLoadFile
        self.theDate = datetime.now().strftime("%Y%m%d-%H%M%S")

        self.runPandas()

    def runPandas(self):
        tngs = pd.read_csv(self.regexFile)
        seq = pd.read_csv(self.seqLoadFile) #delimiter="\t")

        seq.columns = [c.replace(' ', '_') for c in seq.columns]
        tngs.columns = [c.replace(' ', '_') for c in tngs.columns]

        # Starlims sequencing'NGS' workbatch number
        workbatchNo = seq['Container_Name'][0]
        # Remove unwanted columns
        seq = seq.iloc[4:,:2].copy()
        # rename seq columns
        seq.columns = ["Well", "ID"]

        # Get starlims 'amplicon'
        star_amplicon = workbatchNo

        # need to get a dictionary of all sample ID from sequencing load file as that represents what can get
        # imported back into Starlims. Mostly important for the ddPCR mutation details import
        samples = list(seq['ID'].unique())
        del samples[:4]
        samples = [sample[:9] for sample in samples]

        # new column with sample id and mutsurveyor variant
        tngs['id_variant'] = tngs['Folder_number'] + "_" + tngs['MutSurveyor']
        tngs_var = list(tngs['id_variant'].unique())
        tngs_var = [var for var in tngs_var if str(var) != 'nan']

        # new column with sample id and mutation details variant
        tngs['id_mut'] = tngs['Folder_number'] + "_" + tngs['MutDetails']
        tngs_mut = list(tngs['id_mut'].unique())

        # new columns with sample id and genomic nomenclature
        tngs['id_genomic'] = tngs['Folder_number'] + "_" + tngs['Genomic_nomenclature']
        tngs_genomic = list(tngs['id_genomic'].unique())

        # create a dictionary with sample id's and associated variants
        sample_vars = {k:[] for k in samples}
        for sample in samples:
            for variant in tngs_var:
                if sample == variant[:9]:
                    try:
                        sample_vars[sample].append(variant[10:])
                    except:
                        sample_vars[sample] = [variant[10:]]

        # create custom report template
        def create_custom_report():
            f = open(f'{os.getcwd()}/../../output/custom_report' + self.theDate + '.txt', 'w+')
            header = "Warning!\nSample Name\tReference Name\tLane Quality\tROI Coverage\t#nts below threshold\tQuality ROI\tVariant1\tVariant3\tVariant3\tVariant4\n"
            body = ""
            for sample in sample_vars:
                no_vars = len(sample_vars[sample])
                sample_id = sample + star_amplicon + workbatchNo
                if no_vars == 1:
                    body += f"{sample_id}\t\t\t\t\t\t{sample_vars[sample][0]}\n"
                elif no_vars == 2:
                    body += f"{sample_id}\t\t\t\t\t\t{sample_vars[sample][0]}\t{sample_vars[sample][1]}\n"
                elif no_vars == 3:
                    body += f"{sample_id}\t\t\t\t\t\t{sample_vars[sample][0]}\t{sample_vars[sample][1]}\t{sample_vars[sample][2]}\n"
                elif no_vars == 4:
                    body += f"{sample_id}\t\t\t\t\t\t{sample_vars[sample][0]}\t{sample_vars[sample][1]}\t{sample_vars[sample][2]}\t{sample_vars[sample][3]}\n"
                else:
                    body += f"{sample_id}\t\t\t\t\t\t\t\t\t\t\n"
            f.write(header)
            f.write(body)
            f.close()

        create_custom_report()

        # Create Well-Sample dictionary {well:Sample} from seq.csv
        well_sample = {}
        well = list(seq['Well'].unique())
        seqID = [x[:9] for x in list(seq['ID'].unique())]
        for w, s in zip(well, seqID):
            well_sample[w] = s


        # new seq dictionary, nested lists with mutdetails and genomic nomenclature
        seq_mut = {k:[[],[],[]] for k in seqID}
        for sample in seqID:
            for well in well_sample:
                if sample == well_sample[well]:
                    try:
                        seq_mut[sample][0].append(well)
                    except:
                        seq_mut[sample][0] = [well]
            for variant in tngs_mut:
                if sample == variant[:9]:
                    try:
                        seq_mut[sample][1].append(variant[10:])
                    except:
                        seq_mut[sample][1] = [variant[10:]]
            for genomic in tngs_genomic:
                if sample == str(genomic)[:9]:
                    try:
                        seq_mut[sample][2].append(str(genomic)[10:])
                    except:
                        seq_mut[sample][2] = [str(genomic)[10:]]

        # create variant_details import
        def create_variant_import():
            f = open(f'{os.getcwd()}/../../output/variant_import' + self.theDate + '.csv', 'w+')
            header = "Well,Sample,Variant1,Genomic1,Variant2,Genomic2,Variant3,Genomic3\n"
            body = ""
            for sample in seq_mut:
                no_vars = len(seq_mut[sample][1])
                if len(seq_mut[sample][2]) == 0:
                    body += f"{seq_mut[sample][0][0]},{sample},,,,,,\n"
                elif no_vars == 1:
                    body += f"{seq_mut[sample][0][0]},{sample},{seq_mut[sample][1][0]},{seq_mut[sample][2][0]},,,,\n"
                elif no_vars == 2:
                    body += f"{seq_mut[sample][0][0]},{sample},{seq_mut[sample][1][0]},{seq_mut[sample][2][0]},{seq_mut[sample][1][1]},{seq_mut[sample][2][1]},,\n"
                elif no_vars == 3:
                    body += f"{seq_mut[sample][0][0]},{sample},{seq_mut[sample][1][0]},{seq_mut[sample][2][0]},{seq_mut[sample][1][1]},{seq_mut[sample][2][1]},{seq_mut[sample][1][2]},{seq_mut[sample][2][2]}\n"
                else:
                    body += f"{seq_mut[sample][0][0]},{sample},,,,,,\n"
            f.write(header)
            f.write(body)
            f.close()

        create_variant_import()
