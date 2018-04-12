from xml.dom import minidom


class Boleta:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement('SummaryDocuments')
        self.doc.appendChild(root)
        root.setAttribute('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2')
        root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
        root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        root.setAttribute('xmlns:ccts', 'urn:un:unece:uncefact:documentation:2')
        root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
        root.setAttribute('xmlns:qdt', 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2')
        root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
        root.setAttribute('xmlns:udt', 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        return root

    ####
    # Head
    ####

    def UBLVersion(self, ubl_version_id):
        UBLVersion = self.doc.createElement('cbc:UBLVersionID')
        text = self.doc.createTextNode(ubl_version_id)
        UBLVersion.appendChild(text)
        return UBLVersion

    def CustomizationID(self, customization_id):
        Customization = self.doc.createElement('cbc:CustomizationId')
        text = self.doc.createTextNode(customization_id)
        Customization.appendChild(text)
        return Customization

    def SummaryId(self, summary_id):
        Summary = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(summary_id)
        Summary.appendChild(text)
        return Summary

    def ReferenceDate(self, reference_date):
        ReferenceDate = self.doc.createElement('cbc:ReferenceDate')
        text = self.doc.createTextNode(reference_date)
        ReferenceDate.appendChild(text)
        return ReferenceDate

    def IssueDate(self, issue_date):
        IssueDate = self.doc.createElement('cbc:IssueDate')
        text = self.doc.createTextNode(issue_date)
        IssueDate.appendChild(text)
        return IssueDate

    def Note(self, note):
        Note = self.doc.createElement('cbc:note')
        text = self.doc.createTextNode(note)
        Note.appendChild(text)
        return Note

    def SummaryRoot(self, ubl_version_id, customization_id, summary_id,
                    reference_data, issue_date, note):
        SummaryRoot = self.Root()
        SummaryRoot.appendChild(self.UBLVersion(ubl_version_id))
        SummaryRoot.appendChild(self.CustomizationID(customization_id))
        SummaryRoot.appendChild(self.SummaryId(summary_id))
        SummaryRoot.appendChild(self.ReferenceDate(reference_data))
        SummaryRoot.appendChild(self.IssueDate(issue_date))
        SummaryRoot.appendChild(self.Note(note))
        return SummaryRoot

    ####
    # Signature
    ####

    def SignatoryParty(self, signatory_party_id, party_name):
        SignatoryParty = self.doc.createElement('cac:SignatoryParty')

        PartyIdentification = self.doc.createElement('cac:PartyIdentification')
        SignatoryPartyId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(signatory_party_id)
        SignatoryPartyId.appendChild(text)
        PartyIdentification.appendChild(SignatoryPartyId)

        PartyName = self.doc.createElement('cac:PartyName')
        Party_name = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(party_name)
        Party_name.appendChild(text)
        PartyName.appendChild(Party_name)

        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)

        return SignatoryParty

    def DigitalSignature(self, digital_signature_uri):
        DigitalSignature = self.doc.createElement('cac:DigitalSignatureAttachment')

        ExternalReference = self.doc.createElement('cac:ExternalReference')
        ExternalReferenceUri = self.doc.createElement('cbc:URI')
        text = self.doc.createTextNode(digital_signature_uri)
        ExternalReferenceUri.appendChild(text)
        ExternalReference.appendChild(ExternalReferenceUri)

        DigitalSignature.appendChild(ExternalReference)

        return DigitalSignature

    def Signature(self, signature_id, signatory_party_id, party_name, digital_signature_uri):
        Signature = self.doc.createElement('cac:Signature')

        Signature_id = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(signature_id)
        Signature_id.appendChild(text)
        Signature.appendChild(Signature_id)

        signatory_party = self.SignatoryParty(signatory_party_id, party_name)
        Signature.appendChild(signatory_party)
        digital_signature = self.DigitalSignature(digital_signature_uri)
        Signature.appendChild(digital_signature)

        return Signature

    ####
    # Party
    ####

    def AccountingParty(self, registration_name):
        AccountingParty = self.doc.createElement('cac:Party')

        PartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        RegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(registration_name)
        RegistrationName.appendChild(text)
        PartyLegalEntity.appendChild(RegistrationName)
        AccountingParty.appendChild(PartyLegalEntity)

        return AccountingParty

    def AccountingSupplierParty(self, customer_assigned_id, additional_id, registration_name):
        AccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')

        CustomerAssignedId = self.doc.createElement('cbd:CustomerAssignedAccountID')
        text = self.doc.createTextNode(customer_assigned_id)
        CustomerAssignedId.appendChild(text)
        AccountingSupplierParty.appendChild(CustomerAssignedId)

        AdditionalId = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(additional_id)
        AdditionalId.appendChild(text)
        AccountingSupplierParty.appendChild(AdditionalId)

        accounting_party = self.AccountingParty(registration_name)
        AccountingSupplierParty.appendChild(accounting_party)

        return AccountingSupplierParty

    ####
    # Summary Line
    ####

    def SummaryBillingPayment(self, paid_amount, instruction_id):
        SummaryBillingPayment = self.doc.createElement('sac:BillingPayment')

        PaidAmount = self.doc.createElement('cbc:PaidAmount')
        PaidAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(paid_amount)
        PaidAmount.appendChild(text)
        SummaryBillingPayment.appendChild(PaidAmount)

        InstructionId = self.doc.createElement('cbc:InstructionID')
        text = self.doc.createTextNode(instruction_id)
        InstructionId.appendChild(text)
        SummaryBillingPayment.appendChild(InstructionId)

        return SummaryBillingPayment

    def SummaryAllowanceCharge(self, charge_indicator, amount):
        SummaryAllowanceCharge = self.doc.createElement('sac:AllowanceCharge')

        ChargeIndicator = self.doc.createElement('cbc:ChargeIndicator')
        text = self.doc.createTextNode(charge_indicator)
        ChargeIndicator.appendChild(text)
        SummaryAllowanceCharge.appendChild(ChargeIndicator)

        Amount = self.doc.createElement('cbc:Amount')
        Amount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(amount)
        Amount.appendChild(text)
        SummaryAllowanceCharge.appendChild(Amount)

        return SummaryAllowanceCharge

    def SummaryTaxSubtotal(self, tax_amount, tax_id, tax_name, tax_type_code):
        TaxSubtotal = self.doc.createElement('cac:TaxSubtotal')

        TaxAmount = self.doc.createElement('cbc:TaxAmount')
        TaxAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(tax_amount)
        TaxAmount.appendChild(text)
        TaxSubtotal.appendChild(TaxAmount)

        TaxCategory = self.doc.createElement('cac:TaxCategory')
        TaxScheme = self.doc.createElement('cac:TaxScheme')

        TaxId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(tax_id)
        TaxId.appendChild(text)
        TaxScheme.appendChild(TaxId)

        TaxName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(tax_name)
        TaxName.appendChild(text)
        TaxScheme.appendChild(TaxName)

        TaxTypeCode = self.doc.createElement('cbc:TaxTypeCode')
        text = self.doc.createTextNode(tax_type_code)
        TaxTypeCode.appendChild(text)
        TaxScheme.appendChild(TaxTypeCode)
        TaxCategory.appendChild(TaxScheme)

        TaxSubtotal.appendChild(TaxCategory)

        return TaxSubtotal

    def SummaryTaxTotal(self, sub_total):
        TaxTotal = self.doc.createElement('cac:TaxTotal')

        TaxAmount = self.doc.createElement('cbc:TaxAmount')
        TaxAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(sub_total["TaxAmount"])
        TaxAmount.appendChild(text)
        TaxTotal.appendChild(TaxAmount)

        TaxSubTotal = self.SummaryTaxSubtotal(sub_total["TaxAmount"], sub_total["tributo_codigo"],
                                              sub_total["tributo_nombre"], sub_total["tributo_tipo_codigo"])
        TaxTotal.appendChild(TaxSubTotal)

        return TaxTotal

    def SummaryLine(self, line_id, document_type, document_serial, start_document,
                    end_document, total_amount, paid_amount, tax_id, charge_indicator,
                    amount, array_tax_sub_total):
        SummaryLine = self.doc.createElement('sac:SummaryDocumentLine')

        LineId = self.doc.createElement('cbc:LineID')
        text = self.doc.createTextNode(line_id)
        LineId.appendChild(text)
        SummaryLine.appendChild(LineId)

        DocumentType = self.doc.createElement('cbc:DocumentTypeCode')
        text = self.doc.createTextNode(document_type)
        DocumentType.appendChild(text)
        SummaryLine.appendChild(DocumentType)

        DocumentSerial = self.doc.createElement('sac:DocumentSerialID')
        text = self.doc.createTextNode(document_serial)
        DocumentSerial.appendChild(text)
        SummaryLine.appendChild(DocumentSerial)

        StartDocument = self.doc.createElement('sac:StartDocumentNumberID')
        text = self.doc.createTextNode(start_document)
        StartDocument.appendChild(text)
        SummaryLine.appendChild(StartDocument)

        EndDocument = self.doc.createElement('sac:EndDocumentNumberID')
        text = self.doc.createTextNode(end_document)
        EndDocument.appendChild(text)
        SummaryLine.appendChild(EndDocument)

        TotalAmount = self.doc.createElement('sac:TotalAmount')
        TotalAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(total_amount)
        TotalAmount.appendChild(text)
        SummaryLine.appendChild(TotalAmount)

        n = 1
        for billing_amount in paid_amount:
            BillingPayment = self.SummaryBillingPayment(billing_amount, str(n))
            SummaryLine.appendChild(BillingPayment)
            n = n + 1

        AllowanceCharge = self.SummaryAllowanceCharge(charge_indicator, amount)
        SummaryLine.appendChild(AllowanceCharge)

        for tax_sub_total in array_tax_sub_total:
            # print tax_sub_total["tax_amount"]
            TaxTotal = self.SummaryTaxTotal(tax_sub_total)
            SummaryLine.appendChild(TaxTotal)

        return SummaryLine
