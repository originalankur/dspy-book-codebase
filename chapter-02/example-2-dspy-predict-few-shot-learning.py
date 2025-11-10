import dspy

lm = dspy.LM('gemini/gemini-2.0-flash')  # <1>

dspy.configure(lm=lm)

class MedicalCodingSignature(dspy.Signature):
    """Extract ICD-10 codes from clinical notes."""
    clinical_note = dspy.InputField(desc="Clinical documentation")
    icd10_codes = dspy.OutputField(desc="Comma-separated ICD-10 codes")
    rationale = dspy.OutputField(desc="Explanation for code selection")

medical_coder = dspy.Predict(MedicalCodingSignature)

demos = [  # <2>
    dspy.Example(  # <3>
        clinical_note="Patient presents with acute bronchitis, productive cough for 5 days",
        icd10_codes="J20.9",
        rationale="J20.9 is acute bronchitis, unspecified"
    ).with_inputs("clinical_note"),  # <4>
    dspy.Example(
        clinical_note="Type 2 diabetes mellitus with diabetic neuropathy",
        icd10_codes="E11.40",
        rationale="E11.40 covers T2DM with neurological complications"
    ).with_inputs("clinical_note")
]

# Use with demonstrations
medical_coder_with_demos = dspy.Predict(MedicalCodingSignature, demos=demos)  # <5>

# Test on new case
result = medical_coder_with_demos(  # <6>
    clinical_note="Patient diagnosed with hypertensive heart disease with heart failure"
)
print(f"ICD-10 Codes: {result.icd10_codes}")
print(f"Rationale: {result.rationale}")
