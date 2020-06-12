import pandas as pd
import numpy as np
import os
from datetime import datetime
import re

class VariantRegex():

    def __init__(self, starlimsVarPath, exportDir):
        self.starlimsVarPath = starlimsVarPath
        self.exportDir = exportDir
        self.batchNo = re.findall('(?<=_)[0-9]{4}(?=_)',starlimsVarPath)[0]

        self.runPandas()

    def runPandas(self):
        # df_all = pd.read_csv('../data/tNGS_import.csv')
        df_all = pd.read_csv(self.starlimsVarPath)

        # Get ride of unwanted columns and create a new df
        df = df_all.iloc[:,:23].copy()
        df.rename(columns={'WT nucleotides':'Ref', 'Variant nucleotides':'Alt', \
            'Variant type':'varType', 'Inserted nucleotides':'insBases', \
            'Report variant?':'reportVar'}, inplace=True)
        sample_ids = list(x for x in df['Folder number'] if x.startswith("EX"))

        # System functions

        def export_csv(outdir, outname):
            if not os.path.exists(outdir):
                os.mkdir(outdir)

            fullname = os.path.join(outdir, outname)
            df.to_csv(fullname)

        # AminoAcid - Add more code to give the final nomenclature
        # (e.g. replace =, * with ref amino acid and Ter)
        def amino_acid(string):
            amino_acid = str(re.findall("[a-zA-Z]{3}[0-9]+[\_]*[a-zA-Z]*[0-9]*[\=*]*|[?*]", string))
            amino_acid = amino_acid.strip("[]''")
            amino_acid = amino_acid.replace("*", "Ter")
            amino_acid = amino_acid.replace("=", amino_acid[:3])
            return amino_acid

        # Accession number
        df['AccessionNo'] = df['cDNA nomenclature'].apply(lambda x: re.split("\:", str(x), 1)[0])
        # cDNA
        df['cDNANo'] = df['cDNA nomenclature'].apply(lambda x: str(re.findall("[^c\.][0-9]+[+-_]*[0-9]+", str(x))[-1:]).strip("[]''"))
        # AminoAccid
        df['AminoNo'] = df['Protein nomenclature'].apply(lambda x: amino_acid(str(x)))
        # Genomic
        df['GenomicNo'] = df['Genomic nomenclature'].apply(lambda x: str(re.findall("[0-9]+[\-]*[0-9]*", str(x))[-1:]).strip("[]''"))

        # Functions
        def gene_name(gene):
            return re.split("\_", str(gene), 1)[0]

        def single_amino_code(aa3):
            aa_dict = {'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D', 'Cys':'C', \
                'Glu':'E','Gln':'Q', 'Gly':'G', 'His':'H', 'Ile':'I','Leu':'L', \
                'Lys':'K','Met':'M','Phe':'F','Pro':'P','Ser':'S','Thr':'T', \
                'Trp':'W','Tyr':'Y','Val':'V', 'Ter':'X','?':'?'}
            return aa_dict[aa3]

        # need to do something with non-classic zygosity variants
        def zygosity(genotype):
            try:
                genotype = float(genotype)
                if (genotype >= 0.4 and genotype <= 0.7) or (genotype >=1.4 and genotype <= 1.6):
                    return "0/1"
                elif genotype <=0.1:
                    return "1/1"
                else:
                    return genotype
            except:
                return genotype


        def get_exons(gene):
            try:
                gene = gene.split(",")
                exons = [re.findall("_[0-9]+", x)[0].replace("_","") for x in gene]
            except:
                return gene

            if len(exons) == 1:
                return int(exons[0])
            else:
                return exons[0] + "-" + exons[-1]


        def variant_type(varType, insBases):
            if varType == "duplication":
                return "dup"
            elif varType == "deletion":
                return "del"
            elif varType == "insertion":
                return "ins" + insBases
            elif varType == "delins":
                return "delins" + insBases
            else:
                return ""


        def mutation_details(chrom, gene, exon, intron, amino, cdna, ref, alt, genomic, genotype, varType, insBases):
            if pd.isnull(intron):
                coding = "ex"
            else:
                coding = "int"

            if pd.isnull(exon):
                ex_int = get_exons(gene)
            else:
                try:
                    ex_int = int(exon)
                except:
                    ex_int = np.nan
            gene = gene_name(gene)
            genotype = zygosity(genotype)

            varType = variant_type(varType, insBases)

            if pd.isnull(ref) and pd.isnull(exon):
                nucleotide = f"g.{genomic}{varType}"
            elif pd.isnull(ref):
                nucleotide = f"c.{cdna}{varType}"
            else:
                nucleotide = f"c.{cdna}{ref}>{alt}{varType}"

            try:
                amino = amino.replace("=", amino[:3])
                amino = re.sub("[a-zA-Z]{3}fs\*", "fs", amino)
                amino = amino.replace("*", "Ter")
            except:
                pass

            if chrom == "X" or isinstance(genotype, float):
                return f"{gene} {coding}{ex_int} p.{amino} {nucleotide}"
            elif genotype == "0/1":
                return f"{gene} {coding}{ex_int} p.{amino}/N {nucleotide}/N"
            elif genotype == "1/1":
                return f"{gene} {coding}{ex_int} p.{amino}/{amino} {nucleotide}/{nucleotide[2:]}"


        def mut_surveyor(reportVar, chrom, genotype, amino, nucleotide, genomic, ref, alt, insBases, varType):
            if chrom == "X":
                genotype = "1/1"
            else:
                genotype = zygosity(genotype)

            try:
                if len(varType) != 6: varType = varType[:3] # need to check cases of delins
            except:
                pass

            try:
                amino_sep = re.findall('[a-zA-Z]{3}|[\d]+|[_=*]|fs*|fs|[?*]', amino)
            except:
                print("error:", amino)
                pass

            # determine if cDNA or genomic nomenclature should be used
            if (nucleotide == "" and amino == "") and reportVar != "No variant detected":
                genomic = genomic.split("-")
                nucleotide = genomic[0] + "_" + genomic[1]

            # final mutation surveyor output
            if varType == "sub":
                if genotype == "0/1":
                    try:
                        amino = single_amino_code(amino_sep[0])+amino_sep[1]+single_amino_code(amino_sep[0])+single_amino_code(amino_sep[2])
                        return f"c.[{nucleotide}{ref}>{alt}]+[=],p.{amino}"
                    except:
                        return f"c.[{nucleotide}{ref}>{alt}]+[=],p.{amino}"
                elif genotype == "1/1":
                    try:
                        amino = single_amino_code(amino_sep[0])+amino_sep[1]+single_amino_code(amino_sep[2])
                        return f"c.[{nucleotide}{ref}>{alt}]+[{nucleotide}{ref}>{alt}],p.{amino}"
                    except:
                        return f"c.[{nucleotide}{ref}>{alt}]+[{nucleotide}{ref}>{alt}],p.{amino}"
            # insertions
            elif varType == "ins":
                if genotype == "0/1":
                    return f"c.[{nucleotide}_hetins{insBases}"
                elif genotype == "1/1":
                    return f"c.[{nucleotide}_ins{insBases}"
            # delins
            elif varType == "delins":
                if genotype == "0/1":
                    return f"c.[{nucleotide}_hetdelins{insBases}"
                elif genotype == "1/1":
                    return f"c.[{nucleotide}_delins{insBases}"
            #structural variants
            elif varType == "del" or varType == "dup":
                if zygosity(genotype) == "0/1":
                    return f"c.{nucleotide}_het{varType}"
                elif zygosity(genotype) == "1/1":
                    return f"c.{nucleotide}_{varType}"


        df['MutDetails'] = df.apply(lambda x: mutation_details(x.Chromosome, x.Gene, x.Exon, x.Intron, x.AminoNo, x.cDNANo, x.Ref, x.Alt, x.GenomicNo, x.Genotype, x.varType, x.insBases), axis=1)

        df['MutSurveyor'] = df.apply(lambda x: mut_surveyor(x.reportVar, x.Chromosome, x.Genotype, x.AminoNo, x.cDNANo, x.GenomicNo, x.Ref, x.Alt, x.insBases, x.varType), axis=1)

        df = df[df['Folder number'].str.startswith("EX")]

        # set name of export file
        theDate = datetime.now().strftime("%Y%m%d-%H%M%S")
        exportName = f"{self.batchNo}_{theDate}_regex.csv"

        self.fullExportPath = self.exportDir + exportName

        export_csv(self.exportDir, exportName)
