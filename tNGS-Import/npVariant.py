import re

class Variant:

    def __init__(self, ws_main, row):
        self.ws_main = ws_main
        self.row = row

        if self.ws_main.cell(row=self.row, column=5).value != None and \
                self.ws_main.cell(row=self.row, column=6).value != None:
            self.variantPresent = True
            self.gender = self.ws_main.cell(row=self.row, column=3).value.lower()
            self.confirmationRqd = self.get_confirmation()
            self.codingEffect = self.ws_main.cell(row=self.row, column=10).value
            self.variantType = self.ws_main.cell(row=self.row, column=11).value
            self.variantLoc = self.ws_main.cell(row=self.row, column=12).value
            self.variantStatus = self.get_variantStatus()
            self.chr = self.ws_main.cell(row=self.row, column=24).value
            self.gene = self.get_gene()
            self.genotype = self.get_genotype()
            self.gNom = self.get_gNom()
            self.transcript = self.ws_main.cell(row=self.row, column=46).value
            self.exon = self.ws_main.cell(row=self.row, column=13).value
            self.intron = self.ws_main.cell(row=self.row, column=14).value
            self.cNom = self.get_cNom()
            self.pNom = self.amino_acid()
            self.insNucleotides = self.ws_main.cell(row=self.row, column=20).value
        elif self.ws_main.cell(row=self.row, column=5).value != None and \
                self.ws_main.cell(row=self.row, column=6).value == None:
            self.gene = self.get_gene()
            self.variantPresent = True
            self.confirmationRqd = self.get_confirmation()
        else:
            self.variantPresent = False

    def get_gene(self):
        gene = self.ws_main.cell(row=self.row, column=5).value
        if gene.find('_') == -1:
            return gene
        else:
            return gene[:gene.find('_')]

    def get_genotype(self):
        try:
            genotype = float(self.ws_main.cell(row=self.row, column=6).value)
        except ValueError:
            genotype = str(self.ws_main.cell(row=self.row, column=6).value)
        except TypeError:
            return None

        if self.chr != 'X' or self.chr != 'Y': #autosomal gene
            if isinstance(genotype, str):
                if genotype == "0/1":
                    return "Heterozygous"
                if genotype == "1/1":
                    return "Homozygous"
            else:
                if (genotype >= 0.45 and genotype <= 0.55):
                    return "Heterozygous"
                if (genotype >= 0.9 and genotype <= 1.1):
                    return "Homozygous"
        elif self.chr == 'X':
            if isinstance(genotype, str):
                if genotype == "0/1" and self.gender == 'female':
                    return "Heterozygous"
                if genotype == "1/1" and self.gender == 'female':
                    return "Homozygous"
                if genotype == "1/1" and self.gender == 'male':
                    return "Hemizygous"
            else:
                if (genotype >= 0.45 and genotype <= 0.55) and self.gender == 'female':
                    return "Heterozygous"
                if (genotype >= 0.9 and genotype <= 1.1) and self.gender == 'female':
                    return "Homozygous"
                if (genotype >= 0.9 and genotype <= 1.1) and self.gender == 'male':
                    return "Hemizygous"
        elif self.chr == 'Y':
            return "Hemizygous"
        elif self.chr == 'MT':
            return "Heteroplasmy level?"
        else:
            return "Check genotype"

    def get_gNom(self):
        gNom = {"gStart": "", "gEnd": "", "gFull": ""}
        try:
            gNom["gStart"] = self.ws_main.cell(row=self.row, column=44).value
            gNom["gEnd"] = self.ws_main.cell(row=self.row, column=45).value
            gNom["gFull"] = re.split(":g.", self.ws_main.cell(row=self.row, column=7).value)[1]
            return gNom
        except IndexError:
            gNom["gFull"] = re.split(":", self.ws_main.cell(row=self.row, column=7).value)[1]
            return gNom

    def get_cNom2(self):
        try:
            return re.findall("[^c\.][0-9]+[+-_]*[0-9]+", self.ws_main.cell(row=self.row, column=8).value)[-1]
        except:
            return None

    # todo get rid of function?
    def get_cNom(self):
        cNom = {"cStart": "", "cEnd": "", "cFull": "", "cRef": "", "cAlt": "", "cIndel": ""}
        try:
            cNom["cFull"] = re.split(":c.", self.ws_main.cell(row=self.row, column=8).value)[1]
            if cNom["cFull"].find("_") != -1:
                cNom["cStart"] = re.findall("[0-9]+", cNom["cFull"])[0]
                cNom["cEnd"] = re.findall("[0-9]+", cNom["cFull"])[1]
            else:
                cNom["cStart"] = re.findall("[0-9]+", cNom["cFull"])[0]
                cNom["cEnd"] = re.findall("[0-9]+", cNom["cFull"])[0]

            if cNom["cFull"].find(">") != -1:
                cNom["cRef"] = re.split("[>]", cNom["cFull"])[0][-1]
                cNom["cAlt"] = re.split("[>]", cNom["cFull"])[1]
            if cNom["cFull"].find("_") != -1:
                cNom["cIndel"] = re.split("[a-z]+", cNom["cFull"])[-1]
            return cNom
        except:
            return cNom

    # amino acid mark 2
    def amino_acid(self):
        try:
            aminoAcid = self.ws_main.cell(row=self.row, column=9).value
            amino_acid = str(re.findall("[a-zA-Z]{3}[0-9]+[\_]*[a-zA-Z]*[0-9]*[\=*]*|[?*]", aminoAcid))
            amino_acid = amino_acid.strip("[]''")
            amino_acid = amino_acid.replace("=", amino_acid[:3])
            try:
                aa_fs = amino_acid.index("fs*")
                amino_acid = amino_acid.replace(amino_acid[aa_fs - 3:aa_fs + 3], "fs")
            except Exception as e:
                # print("amino_acid error", e)
                pass
            amino_acid = amino_acid.replace("*", "Ter")
            return amino_acid
        except:
            return None

    # todo get rid of this function?
    def get_pNom(self):
        if self.variantLoc == "intron":
            return "p.?"

        aminoAcid = self.ws_main.cell(row=self.row, column=9).value
        pNom = {"pStart": "", "pEnd": "", "pFull": "", "pRef": "", "pAlt": "", "pIndel": ""}
        pNom["pFull"] = aminoAcid[2:].replace("(", "").replace(")", "")
        if pNom["pFull"].find("_") != -1:
            pNom["pStart"] = re.findall("[0-9]+", aminoAcid)[0]
            pNom["pEnd"] = re.findall("[0-9]+", aminoAcid)[1]
        else:
            pNom["pStart"] = re.findall("[0-9]+", aminoAcid)[0]
            pNom["pEnd"] = re.findall("[0-9]+", aminoAcid)[0]

        pNom["pRef"] = re.findall("[a-zA-Z]{3}", aminoAcid)[0]
        if pNom["pFull"].find("=") != -1:
            pNom["pAlt"] = pNom["pRef"]
        elif pNom["pFull"].find("*") != -1:
            pNom["pAlt"] = "Ter"
        else:
            pNom["pAlt"] = re.findall("[a-zA-Z]{3}", aminoAcid)[1]

        # todo pNom Indel not working
        # if pNom["pFull"].find("_") != -1:
        #     for x in re.findall("[a-zA-Z]{3}", aminoAcid)[2:]:
        #         print(type(x), x)
        #         if x != "del" or x != "ins":
        #             pNom["pIndel"] += x
        return pNom

    def get_variantStatus(self):
        status = self.ws_main.cell(row=self.row, column=3).value
        if status.startswith("Novel") or status == "Confirmation reqd" or status.startswith("Sanger"):
            return "Uncertain"
        elif status.startswith("Variant detected"):
            return "Likely pathogenic/Pathogenic"
        else:
            return status

    def get_confirmation(self):
        variant = self.ws_main.cell(row=self.row, column=3).value
        if variant.lower().startswith("sanger") or variant.lower().startswith("confirm"):
            return True
        else:
            return False
