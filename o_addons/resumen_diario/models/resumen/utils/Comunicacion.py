#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom import minidom

class Comunicacion:
    def __init__(self):
        self.doc = minidom.Document()
    
    def Root(self):
        root = self.doc.createElement('VoidedDocuments')
        self.doc.appendChild(root)
        
        root.setAttribute('xmlns', 'urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1')
        root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
        root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
        root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        return root
    
    def VoidedDocumentsLine(self, line_id, tipo_sunat, journal, number, motivo):
        VoidedDocumentsLine = self.doc.createElement('sac:VoidedDocumentsLine')

        LineID = self.doc.createElement('cbc:LineID')
        text = self.doc.createTextNode(str(line_id))
        LineID.appendChild(text)
        VoidedDocumentsLine.appendChild(LineID)

        DocumentTypeCode = self.doc.createElement('cbc:DocumentTypeCode')
        text = self.doc.createTextNode(tipo_sunat)
        DocumentTypeCode.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentTypeCode)

        DocumentSerialID = self.doc.createElement('sac:DocumentSerialID')
        text = self.doc.createTextNode(journal)
        DocumentSerialID.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentSerialID)

        DocumentNumberID = self.doc.createElement('sac:DocumentNumberID')
        text = self.doc.createTextNode(str(number))
        DocumentNumberID.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentNumberID)

        VoidReasonDescription = self.doc.createElement('sac:VoidReasonDescription')
        text = self.doc.createTextNode(motivo)
        VoidReasonDescription.appendChild(text)
        VoidedDocumentsLine.appendChild(VoidReasonDescription)

        return VoidedDocumentsLine

    def firma(self,id):
        UBLExtensions = self.doc.createElement("ext:UBLExtensions")

        UBLExtension = self.doc.createElement("ext:UBLExtension")
        
        ExtensionContent = self.doc.createElement("ext:ExtensionContent")
        
        Signature = self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id",id)
        
        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)
        UBLExtensions.appendChild(UBLExtension)

        return UBLExtensions

    def Signature(self,Id,ruc,razon_social,uri):
        Signature=self.doc.createElement("cac:Signature")
        ID=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(Id)
        ID.appendChild(text)
        Signature.appendChild(ID)

        SignatoryParty=self.doc.createElement("cac:SignatoryParty")
        PartyIdentification=self.doc.createElement("cac:PartyIdentification")
        RUC=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(ruc)
        RUC.appendChild(text)
        PartyIdentification.appendChild(RUC)
        PartyName=self.doc.createElement("cac:PartyName")
        Name=self.doc.createElement("cbc:Name")
        text=self.doc.createTextNode(razon_social)
        Name.appendChild(text)
        PartyName.appendChild(Name)
        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)

        Signature.appendChild(SignatoryParty)

        DigitalSignatureAttachment=self.doc.createElement("cac:DigitalSignatureAttachment")
        ExternalReference=self.doc.createElement("cac:ExternalReference")
        URI=self.doc.createElement("cbc:URI")
        text=self.doc.createTextNode(uri)
        URI.appendChild(text)
        ExternalReference.appendChild(URI)
        DigitalSignatureAttachment.appendChild(ExternalReference)

        Signature.appendChild(DigitalSignatureAttachment)

        return Signature
    # def UBLExtensions(self):
    #     UBLExtensions = self.doc.createElement('ext:UBLExtensions')
    #     UBLExtensions.appendChild(self.UBLExtension)

    #     return UBLExtensions

    # def UBLExtension(self):
    #     UBLExtension = self.doc.createElement('ext:UBLExtension')
    #     ExtensionContent = self.doc.createElement('ext:ExtensionContent')


    #     #UBLExtension.appendChild(self.UBLExtension)

    #     return UBLExtension

    def UBLVersion(self, ubl_version_id):
        UBLVersion = self.doc.createElement('cbc:UBLVersionID')
        text = self.doc.createTextNode(ubl_version_id)
        UBLVersion.appendChild(text)
        
        return UBLVersion
    
    def CustomizationID(self, customization_id):
        Customization = self.doc.createElement('cbc:CustomizationID')
        text = self.doc.createTextNode(str(customization_id))
        Customization.appendChild(text)
        
        return Customization
    
    def SummaryId(self, summary_id):
        SummaryID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(summary_id)
        SummaryID.appendChild(text)

        return SummaryID
    
    ## Fecha de emision de los documentos
    def ReferenceDate(self, reference_date):
        ReferenceDate = self.doc.createElement('cbc:ReferenceDate')
        text = self.doc.createTextNode(reference_date)
        ReferenceDate.appendChild(text)
        return ReferenceDate
    
    ## Fecha de generacion del resumen
    def IssueDate(self, issue_date):
        IssueDate = self.doc.createElement('cbc:IssueDate')
        text = self.doc.createTextNode(issue_date)
        IssueDate.appendChild(text)

        return IssueDate

    def Note(self, note):
        Note = self.doc.createElement('cbc:Note')
        text = self.doc.createTextNode(note)
        Note.appendChild(text)

        return Note

    def SummaryRoot(self, rootXML, ubl_version_id, customization_id, summary_id, reference_date, issue_date):
        SummaryRoot = rootXML

        SummaryRoot.appendChild(self.UBLVersion(ubl_version_id))
        SummaryRoot.appendChild(self.CustomizationID(customization_id))
        SummaryRoot.appendChild(self.SummaryId(summary_id))
        SummaryRoot.appendChild(self.ReferenceDate(reference_date))
        SummaryRoot.appendChild(self.IssueDate(issue_date))

        return SummaryRoot

    def cacAccountingSupplierParty(self, num_doc_ident, tipo_doc_ident, nombre_comercial):
        cacAccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')

        # Numero de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)

        # tipo de documento de identidad
        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(tipo_doc_ident)
        cbcAdditionalAccountID.appendChild(text)
        
        # Party
        cacParty = self.doc.createElement('cac:Party')
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        
        # Nombre Comercial
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(str(nombre_comercial))
        cbcRegistrationName.appendChild(text)
        
        cacPartyLegalEntity.appendChild(cbcRegistrationName)
            
        cacParty.appendChild(cacPartyLegalEntity)

        cacAccountingSupplierParty.appendChild(cbcCustomerAssignedAccountID)
        cacAccountingSupplierParty.appendChild(cbcAdditionalAccountID)
        cacAccountingSupplierParty.appendChild(cacParty)

        return cacAccountingSupplierParty
    
    
    def sendBill(self,username,password,namefile,contentfile):
        Envelope=self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv","http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser","http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header=self.doc.createElement("soapenv:Header")
        Security=self.doc.createElement("wsse:Security")
        UsernameToken=self.doc.createElement("wsse:UsernameToken")
        Username=self.doc.createElement("wsse:Username")
        text=self.doc.createTextNode(username)
        Username.appendChild(text)
        Password=self.doc.createElement("wsse:Password")
        text=self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body=self.doc.createElement("soapenv:Body")
        sendBill=self.doc.createElement("ser:sendSummary")
        fileName=self.doc.createElement("fileName")
        text=self.doc.createTextNode(namefile)
        fileName.appendChild(text)
        contentFile=self.doc.createElement("contentFile")
        text=self.doc.createTextNode(contentfile)
        contentFile.appendChild(text)
        sendBill.appendChild(fileName)
        sendBill.appendChild(contentFile)
        Body.appendChild(sendBill)
        Envelope.appendChild(Body)

        return Envelope

    def getStatus(self,username,password,ticket_r):
        Envelope=self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv","http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser","http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header=self.doc.createElement("soapenv:Header")
        Security=self.doc.createElement("wsse:Security")
        UsernameToken=self.doc.createElement("wsse:UsernameToken")
        Username=self.doc.createElement("wsse:Username")
        text=self.doc.createTextNode(username)
        Username.appendChild(text)
        Password=self.doc.createElement("wsse:Password")
        text=self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body=self.doc.createElement("soapenv:Body")
        getStatus=self.doc.createElement("ser:getStatus")
        ticket=self.doc.createElement("ticket")
        text=self.doc.createTextNode(ticket_r)
        ticket.appendChild(text)
        getStatus.appendChild(ticket)
        Body.appendChild(getStatus)
        Envelope.appendChild(Body)

        return Envelope