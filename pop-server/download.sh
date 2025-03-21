#!/bin/bash

if [ "$1" == "" ]; then
  echo "$0: Please provide a terminology"
  exit 1
fi
if [ -f ".env" ];then
    source ".env"
fi

# Set proxy options if PROXY_URL_HTTPS is defined
WGET_PROXY_OPTIONS=""
if [ -n "$HTTPS_PROXY_URL" ]; then
  WGET_PROXY_OPTIONS="-e use_proxy=yes -e https_proxy=$HTTPS_PROXY_URL  -e http_proxy=$HTTP_PROXY_URL --ca-certificate=$CA_BUNDLE_CERT"
fi

TERMINOLOGY=$1
DATA_DIR=$EXTERNAL_DATA_DIR

mkdir -p $DATA_DIR

download_cvx() {
  # Local variables
  DOWNLOAD_URL=https://www2a.cdc.gov/vaccines/iis/iisstandards/downloads/cvx.txt
  DOWNLOAD_FILE="${DATA_DIR}/cvx.txt"
  PROCESSED_FILE="${DATA_DIR}/cvx.tsv"

  echo ""
  echo "Downloading CVX files"
  echo "-----------------------------------"
  rm -f $PROCESSED_FILE
  wget  $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL 
  printf "CVX Code\\tCVX Short Description\\tFull Vaccine Name\\tNote\\tVaccineStatus\\tnonvaccine\\tupdate_date\\n" > $PROCESSED_FILE
  sed 's/|/\t/g' $DOWNLOAD_FILE >> $PROCESSED_FILE
  rm -r $DOWNLOAD_FILE
  echo -e "\n✓ Data processing completed."
  echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}


download_atc() {
  # Local variables
  DOWNLOAD_URL=https://raw.githubusercontent.com/fabkury/atcd/9c25d1d168e38b935ad19f2b06def0b315fce0e1/WHO%20ATC-DDD%202024-07-31.csv
  DOWNLOAD_FILE="${DATA_DIR}/atc.csv"
  echo ""
  echo "Downloading WHO ATC files"
  echo "-----------------------------------"
  wget  $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL 
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_hgnc() {
	# Local variables
	DOWNLOAD_URL=https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt
	DOWNLOAD_FILE=${DATA_DIR}/hgnc.tsv
	echo ""
	echo "Downloading HGNC files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_so() {
	# Local variables
	DOWNLOAD_URL=https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/refs/heads/master/Ontology_Files/so.obo
	DOWNLOAD_FILE=${DATA_DIR}/so.obo
	echo ""
	echo "Downloading SO files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_oncotree() {
	# Local variables
	DOWNLOAD_URL=https://oncotree.mskcc.org/api/tumorTypes/tree
	DOWNLOAD_FILE=${DATA_DIR}/oncotree.json
	echo ""
	echo "Downloading OncoTree files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS --no-cache -U "Mozilla/4.0" -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_icdo3topo() {
	# Local variables
	DOWNLOAD_URL=https://raw.githubusercontent.com/luisfabib/icd10_2019_data/refs/heads/main/icdo3/icdo3.2_topography.tsv
	DOWNLOAD_FILE=${DATA_DIR}/icdo3topo.tsv
	echo ""
	echo "Downloading ICD-O-3 Topography files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS --no-cache -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_icdo3morph() {
	# Local variables
	DOWNLOAD_URL=https://raw.githubusercontent.com/luisfabib/icd10_2019_data/refs/heads/main/icdo3/icdo3.2_morphology.tsv
	DOWNLOAD_FILE=${DATA_DIR}/icdo3morph.tsv
	echo ""
	echo "Downloading ICD-O-3 Morphology files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS --no-cache -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_icdo3diff() {
	# Local variables
	DOWNLOAD_URL=https://raw.githubusercontent.com/luisfabib/icd10_2019_data/refs/heads/main/icdo3/icdo3.2_differentiation.tsv
	DOWNLOAD_FILE=${DATA_DIR}/icdo3diff.tsv
	echo ""
	echo "Downloading ICD-O-3 Differentiation files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS --no-cache -O $DOWNLOAD_FILE $DOWNLOAD_URL
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_icd10() {
	# Local variables
	DOWNLOAD_URL=https://raw.githubusercontent.com/luisfabib/icd10_2019_data/refs/heads/main/icd10/icd10_2019.tsv
    DOWNLOAD_FILE=${DATA_DIR}/icd10temp.tsv
    PROCESSED_FILE=${DATA_DIR}/icd10.tsv
	echo ""
	echo "Downloading ICD-10 files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
    printf "code\\tdisplay\\n" > $PROCESSED_FILE
    cat $DOWNLOAD_FILE >> $PROCESSED_FILE
    rm $DOWNLOAD_FILE
  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


download_icd10cm() {
	# Local variables
	DOWNLOAD_URL=https://www.cms.gov/files/zip/2025-code-descriptions-tabular-order.zip
	DOWNLOAD_FILE=$DATA_DIR/icd10cm.zip
	TEMP_DIR=$DATA_DIR/.icd10cm
	PROCESSED_FILE=$DATA_DIR/icd10cm.txt
	echo ""
	echo "Downloading ICD-10-CM files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  unzip $DOWNLOAD_FILE -d $TEMP_DIR
  rm $DOWNLOAD_FILE
  mv $TEMP_DIR/icd10cm_codes_20*.txt $PROCESSED_FILE
  sed -i '1iterm' $PROCESSED_FILE
  rm -r $TEMP_DIR
  echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}


download_icd10pcs() {
	# Local variables
	DOWNLOAD_URL=https://www.cms.gov/files/zip/2025-icd-10-pcs-codes-file.zip
	DOWNLOAD_FILE=$DATA_DIR/icd10pcs.zip
	TEMP_DIR=$DATA_DIR/.icd10pcs
	PROCESSED_FILE=$DATA_DIR/icd10pcs.txt
	echo ""
	echo "Downloading ICD-10-PCS files"
	echo "-----------------------------------"
	wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  unzip $DOWNLOAD_FILE -d $TEMP_DIR
  rm $DOWNLOAD_FILE
  mv $TEMP_DIR/icd10pcs_codes_20*.txt $PROCESSED_FILE
  sed -i '1iterm' $PROCESSED_FILE
  rm -r $TEMP_DIR
  echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}

download_ncit() {
	# Local variables
	DOWNLOAD_URL=https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Thesaurus_24.09e.FLAT.zip
	DOWNLOAD_FILE=$DATA_DIR/ncit.zip
	PROCESSED_FILE=$DATA_DIR/ncit.tsv
	echo ""
	echo "Downloading NCI Thesaurus files"
	echo "-----------------------------------"
  wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  unzip $DOWNLOAD_FILE
  echo -e "code\\tconcept IRI	parents	synonyms\\tdefinition\\tdisplay name\\tconcept status\\tsemantic type\\tconcept in subset" > $PROCESSED_FILE
  cat Thesaurus.txt >> $PROCESSED_FILE
  rm $DOWNLOAD_FILE Thesaurus.txt
  echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}

download_ncit_antineoplastic() {
	# Local variables
	DOWNLOAD_URL=https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Drug_or_Substance/Antineoplastic_Agent.txt
	DOWNLOAD_FILE=$DATA_DIR/ncit_antineoplastic.tsv
	echo ""
	echo "Downloading NCI Thesaurus Antineoplastic subset files"
	echo "-----------------------------------"
  wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  # Convert to UTF-8 (if needed)
  ENCODING=$(file -bi "$DOWNLOAD_FILE" | awk -F "=" '{print $2}')
  if [ "$ENCODING" != "utf-8" ]; then
      iconv -f "$ENCODING" -t "UTF-8" "$DOWNLOAD_FILE" -o "${DOWNLOAD_FILE}.utf8"
      mv "${DOWNLOAD_FILE}.utf8" $DOWNLOAD_FILE
      echo "File converted to UTF-8."
  else
      echo "File is already UTF-8 encoded."
  fi

  echo -e "\n✓ Download complete. Saved data to $DOWNLOAD_FILE.\n"
}


process_loinc() {
	# Local variables
	TEMP_DIR=$DATA_DIR/.loinc
	echo ""
	echo "Processing LOINC files"
	echo "-----------------------------------"
  if [ ! -f $LOINC_ZIPFILE_PATH ]; then
      echo -e "ERROR FILE NOT FOUND:\nPlease download the LOINC_*.zip file from (requires a LOINC login):\n\n\thttps://loinc.org/download/loinc-complete/ \n\nand specify the location of the zip file with the LOINC_ZIPFILE_PATH variable.\n"
      exit 1
  fi  
  echo "unzip $LOINC_ZIPFILE_PATH -d $TEMP_DIR "
  unzip $LOINC_ZIPFILE_PATH -d $TEMP_DIR 
  mv $TEMP_DIR/AccessoryFiles/LinguisticVariants/deDE15LinguisticVariant.csv $DATA_DIR/loinc_deDE15.csv
  mv $TEMP_DIR/AccessoryFiles/LinguisticVariants/frFR18LinguisticVariant.csv $DATA_DIR/loinc_frFR18.csv
  mv $TEMP_DIR/AccessoryFiles/LinguisticVariants/itIT16LinguisticVariant.csv $DATA_DIR/loinc_itIT16.csv

  mv $TEMP_DIR/LoincTable/Loinc.csv $DATA_DIR/loinc.csv

  mv $TEMP_DIR/AccessoryFiles/AnswerFile/AnswerList.csv $DATA_DIR/loinc_answer_lists.csv
  mv $TEMP_DIR/AccessoryFiles/ComponentHierarchyBySystem/ComponentHierarchyBySystem.csv $DATA_DIR/loinc_parts.csv

  rm -r $TEMP_DIR
  echo -e "\n✓ Processing complete. Saved data to multiple loinc*.csv files.\n"
}

process_snomedct() {
	# Local variables
	TEMP_DIR=$DATA_DIR/.snomed
	echo ""
	echo "Processing SNOMED-CT files"
	echo "-----------------------------------"
  if [ ! -f $SNOMED_ZIPFILE_PATH ]; then
      echo -e "ERROR FILE NOT FOUND:\nPlease download the SNOMEDCT_International_*.zip file from (requires a LOINC login):\n\n\thttps://mlds.ihtsdotools.org/#/viewReleases/viewRelease/167 \n\nand specify the location of the zip file with the SNOMED_ZIPFILE_PATH variable.\n"
      exit 1
  fi  
  mkdir $TEMP_DIR
  unzip $SNOMED_ZIPFILE_PATH -d $DATA_DIR
  mv $DATA_DIR/SnomedCT_* $TEMP_DIR
  mv $TEMP_DIR/Snapshot/Terminology/sct2_Description_Snapshot-en_INT_* $DATA_DIR/snomedct.tsv 
  mv $TEMP_DIR/Snapshot/Terminology/sct2_Relationship_Snapshot_INT_* $DATA_DIR/snomedct_relations.tsv
  rm -r $TEMP_DIR
  echo -e "\n✓ Processing complete. Saved data to multiple snomed*.csv files.\n"
}


download_ctcae() {
	# Local variables
	DOWNLOAD_URL=https://ctep.cancer.gov/protocolDevelopment/electronic_applications/docs/CTCAE_v5.0.xlsx
	DOWNLOAD_FILE=$DATA_DIR/ctcae.xlsx
	PROCESSED_FILE=$DATA_DIR/ctcae.csv
	echo ""
	echo "Downloading CTCAE files"
	echo "-----------------------------------"
  wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  xlsx2csv $DOWNLOAD_FILE $PROCESSED_FILE
  echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}

download_ucum() {
	# Local variables
	DOWNLOAD_URL=https://github.com/ucum-org/ucum/raw/refs/heads/main/common-units/TableOfExampleUcumCodesForElectronicMessaging.xlsx
	DOWNLOAD_FILE=$DATA_DIR/ucum.xlsx
	TEMP_FILE=$DATA_DIR/.ucum.csv
	PROCESSED_FILE=$DATA_DIR/ucum.csv
	echo ""
	echo "Downloading UCUM (common) files"
	echo "-----------------------------------"
  wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  xlsx2csv $DOWNLOAD_FILE $TEMP_FILE
  tail -n +5 $TEMP_FILE > tmp && mv tmp $TEMP_FILE
  echo "Row,UCUM_CODE,Description,Comment,Last Updated,Version correction published,Corrected by,Row correction, Previous UCUM version,Description of Change Made" > $PROCESSED_FILE
  cat $TEMP_FILE >> $PROCESSED_FILE
  rm $DOWNLOAD_FILE $TEMP_FILE
    echo -e "\n✓ Download complete. Saved data to $PROCESSED_FILE.\n"
}

download_hta() {
	# Local variables
	DOWNLOAD_URL=https://terminology.hl7.org/package.tgz
	DOWNLOAD_FILE=$DATA_DIR/hta.tgz
	OUTPUT_DIR=$DATA_DIR/hta
	echo ""
	echo "Downloading HL7 Terminology Authority files"
	echo "-----------------------------------"
  wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
  tar -xvzf $DOWNLOAD_FILE -C $DATA_DIR
  mv $DATA_DIR/package $OUTPUT_DIR
  rm $DOWNLOAD_FILE
  echo -e "\n✓ Download complete. Saved all files to $OUTPUT_DIR.\n"
}

download_ch-term() {
    # Local variables
    DOWNLOAD_URL=https://fhir.ch/ig/ch-term/package.tgz
    DOWNLOAD_FILE=$DATA_DIR/ch-term.tgz
    OUTPUT_DIR=$DATA_DIR/ch-term
    echo ""
    echo "Downloading CH-Term IG files"
    echo "-----------------------------------"
    wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
    tar -xvzf $DOWNLOAD_FILE -C $DATA_DIR
    mv $DATA_DIR/package $OUTPUT_DIR
    rm $DOWNLOAD_FILE
    echo -e "\n✓ Download complete. Saved all files to $OUTPUT_DIR.\n"
}

download_genomics-reporting() {
    # Local variables
    DOWNLOAD_URL=https://hl7.org/fhir/uv/genomics-reporting/definitions.json.zip
    DOWNLOAD_FILE=$DATA_DIR/genomics-reporting.tgz
    OUTPUT_DIR=$DATA_DIR/genomics-reporting
    echo ""
    echo "Downloading Genomics Reporting IG files"
    echo "-----------------------------------"
    wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
    unzip $DOWNLOAD_FILE -d $OUTPUT_DIR -y
    rm $DOWNLOAD_FILE
    echo -e "\n✓ Download complete. Saved all files to $OUTPUT_DIR.\n"
}


download_mcode() {
    # Local variables
    DOWNLOAD_URL=https://hl7.org/fhir/us/mcode/definitions.json.zip
    DOWNLOAD_FILE=$DATA_DIR/mcode.tgz
    OUTPUT_DIR=$DATA_DIR/mcode
    echo ""
    echo "Downloading mCODE IG files"
    echo "-----------------------------------"
    wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
    unzip $DOWNLOAD_FILE -d $OUTPUT_DIR -y
    rm $DOWNLOAD_FILE
    echo -e "\n✓ Download complete. Saved all files to $OUTPUT_DIR.\n"
}

download_rxnorm() {
    # Local variables
    DOWNLOAD_URL="https://rxnav.nlm.nih.gov/REST/allconcepts.json?tty=ALL"
    DOWNLOAD_FILE=$DATA_DIR/rxnorm.json
    PROCESSED_FILE=$DATA_DIR/rxnorm.csv
    echo ""
    echo "Downloading RxNorm files"
    echo "-----------------------------------"
    wget $WGET_PROXY_OPTIONS -O $DOWNLOAD_FILE $DOWNLOAD_URL
    echo "rxcui,name,tty" > "$PROCESSED_FILE"
    echo "rxcui,name,tty" > "$PROCESSED_FILE"
    jq -r '.minConceptGroup.minConcept[] | [.rxcui, .name, .tty] | @csv' "$DOWNLOAD_FILE" >> "$PROCESSED_FILE"
    rm $DOWNLOAD_FILE
    echo -e "\n✓ Download complete. Saved to $PROCESSED_FILE.\n"
}

# Main logic based on the terminology argument
case "$TERMINOLOGY" in
  cvx) download_cvx;;
  hgnc) download_hgnc;;
  hgnc-group) download_hgnc;;
  so) download_so;;
  icdo3topo) download_icdo3topo;;
  icdo3morph) download_icdo3morph;;
  icdo3diff) download_icdo3diff;;
  oncotree) download_oncotree;;
  icd10) download_icd10;;
  icd10cm) download_icd10cm;;
  icd10pcs) download_icd10pcs;;
  ctcae) download_ctcae;;
  ncit) download_ncit;;
  ncit-antineoplastic) download_ncit_antineoplastic;;
  loinc) process_loinc;;
  rxnorm) download_rxnorm;;
  snomedct) process_snomedct;;
  ucum) download_ucum;;
  hta) download_hta;;
  atc) download_atc;;
  ch-term) download_ch-term;;
  mcode) download_mcode;;
  genomics-reporting) download_genomics-reporting;;
  *)
    echo "Error: Unknown terminology '$TERMINOLOGY'."
    exit 1
    ;;
esac