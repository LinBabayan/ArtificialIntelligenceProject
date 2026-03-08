import os
import sqlite3
import re
from owlready2 import *

# Use your installed Java (needed for sync_reasoner)
owlready2.JAVA_EXE = r"C:\Program Files\Java\jdk-25\bin\java.exe"

# ===== FILES (same folder) =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONTO_FILE = os.path.join(BASE_DIR, "medical_ontology.rdf")
DB_FILE = os.path.join(BASE_DIR, "medical_ontology.db")


# ===== REMOVE WebProtégé URN IMPORTS (prevents load crash) =====
def make_imports_safe_copy(src_path: str) -> str:
    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    # Remove RDF/XML owl:imports tags like: <owl:imports rdf:resource="urn:webprotege:ontology:..."/>
    text = re.sub(r'<owl:imports[^>]*?/>\s*', '', text)
    # Remove possible paired form
    text = re.sub(r'<owl:imports\b[^>]*>\s*</owl:imports>\s*', '', text)
    safe_path = os.path.join(os.path.dirname(src_path), "medical_ontology_clean.rdf")
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(text)
    return safe_path


# ===== LOAD ONTOLOGY =====
try:
    safe_onto = make_imports_safe_copy(ONTO_FILE)
    onto = get_ontology(safe_onto).load()
    print("✅ Logic Loaded Successfully.")
except Exception as e:
    print(f"❌ Load Error: {e}")
    raise SystemExit(1)


# ===== FIND ENTITIES BY LABEL OR IRI FRAGMENT =====
def find_entity(label_or_name: str):
    ent = onto.search_one(label=label_or_name)
    if not ent:
        ent = onto.search_one(iri=f"*{label_or_name}*")
    return ent


# Owlready2 may use internal IDs (e.g., RBR9q...) as the python attribute name.
# This helper returns the correct attribute name to use on individuals.
def prop_attr(prop):
    return getattr(prop, "python_name", None) or prop.name


# ===== YOUR CLASS NAMES (from screenshot) =====
BodyPartClass        = find_entity("BodyPart")
DiseaseClass         = find_entity("Disease")
FemaleOnlyDiseaseCls = find_entity("FemaleOnlyDisease")
MaleOnlyDiseaseCls   = find_entity("MaleOnlyDisease")
PatientClass         = find_entity("Patient")
SexClass             = find_entity("Sex")
SymptomClass         = find_entity("Symptom")

# ===== YOUR OBJECT PROPERTY NAMES (from screenshot) =====
hasCondition        = find_entity("hasCondition")        # Patient -> Disease
hasLocation         = find_entity("hasLocation")         # Disease -> BodyPart
hasObservedSymptom  = find_entity("hasObservedSymptom")  # (optional)
hasSex              = find_entity("hasSex")              # Patient -> Sex
hasSymptom          = find_entity("hasSymptom")          # Disease -> Symptom
isConditionOf       = find_entity("isConditionOf")       # Disease -> Patient (optional inverse)

# ===== REQUIRED CHECKS =====
required = [
    ("BodyPart", BodyPartClass),
    ("Disease", DiseaseClass),
    ("Patient", PatientClass),
    ("Sex", SexClass),
    ("Symptom", SymptomClass),
    ("hasCondition", hasCondition),
    ("hasLocation", hasLocation),
    ("hasSex", hasSex),
    ("hasSymptom", hasSymptom),
]
missing = [name for name, ent in required if ent is None]
if missing:
    print("❌ Missing in ontology:", ", ".join(missing))
    print("Fix: in Protégé ensure the labels/names match exactly.")
    raise SystemExit(1)

print(f"🎯 Mapped classes OK (Disease ID: {DiseaseClass.name})")


# ===== DB -> ONTOLOGY MAPPING =====
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with onto:
        # ---- Sex individuals ----
        sex_individuals = {}  # sex_id -> individual
        cursor.execute("SELECT id, type FROM Sex")
        for sex_id, sex_type in cursor.fetchall():
            ind = SexClass(f"Sex_{sex_id}")
            sex_individuals[sex_id] = ind

        # ---- BodyPart individuals ----
        body_parts = {}  # body_part_id -> individual
        cursor.execute("SELECT id, name FROM BodyPart")
        for bp_id, bp_name in cursor.fetchall():
            bp = BodyPartClass(f"BodyPart_{bp_id}")
            body_parts[bp_id] = bp

        # ---- Symptom individuals ----
        symptoms = {}  # symptom_id -> individual
        cursor.execute("SELECT id, name FROM Symptom")
        for s_id, s_name in cursor.fetchall():
            s = SymptomClass(f"Symptom_{s_id}")
            symptoms[s_id] = s

        # ---- Disease individuals ----
        diseases = {}  # disease_id -> individual
        cursor.execute("SELECT id, name, category, body_part_id FROM Disease")
        for d_id, d_name, category, body_part_id in cursor.fetchall():
            d = DiseaseClass(f"Disease_{d_id}")
            diseases[d_id] = d

            # Optional: assert sex-specific subclass based on DB category string
            # category examples: 'FemaleOnly', 'MaleOnly', 'General'
            if category:
                cat = str(category).lower()
                if ("female" in cat) and (FemaleOnlyDiseaseCls is not None):
                    d.is_a.append(FemaleOnlyDiseaseCls)
                if ("male" in cat) and (MaleOnlyDiseaseCls is not None):
                    d.is_a.append(MaleOnlyDiseaseCls)

            # Disease -> hasLocation -> BodyPart
            if body_part_id is not None and body_part_id in body_parts:
                setattr(d, prop_attr(hasLocation), [body_parts[body_part_id]])

        # ---- Disease -> hasSymptom -> Symptom ----
        cursor.execute("SELECT disease_id, symptom_id FROM Disease_Symptom")
        for d_id, s_id in cursor.fetchall():
            if d_id in diseases and s_id in symptoms:
                getattr(diseases[d_id], prop_attr(hasSymptom)).append(symptoms[s_id])

        # ---- Patient individuals ----
        patients = {}  # patient_id -> individual
        cursor.execute("SELECT id, name, sex_id FROM Patient")
        for p_id, p_name, sex_id in cursor.fetchall():
            p = PatientClass(f"Patient_{p_id}")
            patients[p_id] = p

            # Patient -> hasSex -> Sex
            if sex_id is not None and sex_id in sex_individuals:
                setattr(p, prop_attr(hasSex), [sex_individuals[sex_id]])

        # ---- Patient -> hasCondition -> Disease ----
        # optional inverse Disease -> isConditionOf -> Patient
        cursor.execute("SELECT patient_id, disease_id FROM Patient_Diagnosis")
        for p_id, d_id in cursor.fetchall():
            if p_id in patients and d_id in diseases:
                getattr(patients[p_id], prop_attr(hasCondition)).append(diseases[d_id])

                if isConditionOf is not None:
                    getattr(diseases[d_id], prop_attr(isConditionOf)).append(patients[p_id])

    conn.close()
    print("📥 Database data mapped to ontology individuals.")

except Exception as e:
    print(f"❌ ERROR: {e}")
    raise SystemExit(1)


# ===== RUN REASONER =====
print("🧠 Starting Reasoner...")
try:
    sync_reasoner(infer_property_values=True)
    print("✨ Reasoning Complete!")
except Exception as e:
    print(f"⚠️ Reasoner issue: {e}")

# ===== SAVE OUTPUT =====
out_path = os.path.join(BASE_DIR, "medical_final.owl")
onto.save(file=out_path, format="rdfxml")
print(f"💾 Saved! Open this in Protégé: {out_path}")