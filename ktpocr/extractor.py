import cv2
import json
import re
import numpy as np
import pytesseract
import matplotlib.pyplot as plt
from ktpocr.form import KTPInformation
from PIL import Image


class KTPOCR(object):
    def __init__(self, image):
        self.image = cv2.imread(image)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.th, self.threshed = cv2.threshold(
            self.gray, 127, 255, cv2.THRESH_TRUNC)
        self.result = KTPInformation()
        self.master_process()

    def process(self, image):
        raw_extracted_text = pytesseract.image_to_string(
            (self.threshed), lang="ind")
        return raw_extracted_text

    def word_to_number_converter(self, word):
        word_dict = {
            '|': "1"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def nik_extract(self, word):
        word_dict = {
            'b': "6",
            'e': "2",
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def extract(self, extracted_result):
        # print(extracted_result.replace('\n', ' -- '))
        for word in extracted_result.split("\n"):
            print(word)
            if "NIK" in word:
                try:
                    word = word.split(':')
                    self.result.nik = self.nik_extract(
                        word[-1].replace(" ", ""))
                except:
                    self.result.nik = "-"
                continue

            if "Nama" in word:
                try:
                    word = word.split(':')
                    self.result.nama = word[-1].replace('Nama ', '')
                except:
                    self.result.nama = "-"
                continue

            if "Tempat" in word:
                try:
                    word = word.split(':')
                    self.result.tanggal_lahir = re.search(
                        "([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])[0]
                    self.result.tempat_lahir = word[-1].replace(
                        self.result.tanggal_lahir, '')
                except:
                    self.result.tempat_lahir = "-"
                continue

            if 'Darah' in word:
                try:
                    self.result.jenis_kelamin = re.search(
                        "(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)[0]
                    word = word.split(':')
                    self.result.golongan_darah = re.search(
                        "(O|A|B|AB)", word[-1])[0]
                except:
                    self.result.golongan_darah = '-'
            if 'Alamat' in word:
                try:
                    self.result.alamat = self.word_to_number_converter(
                    word).replace("Alamat ", "")
                except:
                    self.result.alamat = "-"
            if 'NO.' in word:
                try:
                    self.result.alamat = self.result.alamat + ' '+word
                except:
                    self.result.alamat = "-"
            if "Kecamatan" in word:
                try:
                    self.result.kecamatan = word.split(':')[1].strip()
                except:
                    self.result.kecamatan = "-"
            if "Desa" in word:
                try:
                    wrd = word.split()
                    desa = []
                    for wr in wrd:
                        if not 'desa' in wr.lower():
                            desa.append(wr)
                    self.result.kelurahan_atau_desa = ''.join(wr)
                except:
                    self.result.kelurahan_atau_desa = "-"
            if 'Kewarganegaraan' in word:
                try:
                    self.result.kewarganegaraan = word.split(':')[1].strip()
                except:
                    self.result.kewarganegaraan = "-"
            if 'Pekerjaan' in word:
                try:
                    wrod = word.split()
                    pekerjaan = []
                    for wr in wrod:
                        if not '-' in wr:
                            pekerjaan.append(wr)
                    self.result.pekerjaan = ' '.join(
                        pekerjaan).replace('Pekerjaan', '').strip()
                except:
                    self.result.pekerjaan = "-"
            if 'Agama' in word:
                try:
                    self.result.agama = word.replace('Agama', "").strip()
                except:
                    self.result.agama = "-"
            if 'Perkawinan' in word:
                try:
                    self.result.status_perkawinan = word.split(':')[1]
                except:
                    self.result.status_perkawinan = "-"
            if "RTRW" in word:
                print(word)
                word = word.replace("RTRW", '')

                try:
                    self.result.rt = word.split('/')[0].strip()
                except:
                    self.result.rt = word.split(' ')[0].strip()

                try:
                    self.result.rw = word.split('/')[1].strip()
                except:
                    self.result.rw = word.split(' ')[1].strip()

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return json.dumps(self.result.__dict__, indent=4)
