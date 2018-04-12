from xml.dom import minidom


class NotaDebito:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement('DebitNote')
        self.doc.appendChild(root)
        root.setAttribute('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2')
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
        Customization = self.doc.createElement('cbc:CustomizationID')
        text = self.doc.createTextNode(customization_id)
        Customization.appendChild(text)
        return Customization

    def SummaryId(self, summary_id):
        Summary = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(summary_id)
        Summary.appendChild(text)
        return Summary

    def IssueDate(self, issue_date):
        IssueDate = self.doc.createElement('cbc:IssueDate')
        text = self.doc.createTextNode(issue_date)
        IssueDate.appendChild(text)
        return IssueDate

    def DocumentCurrency(self, currency_code):
        DocumentCurrency = self.doc.createElement('cbc:DocumentCurrencyCode')
        text = self.doc.createTextNode(currency_code)
        DocumentCurrency.appendChild(text)
        return DocumentCurrency

    def NotaDebitoRoot(self,root,ubl_version_id, customization_id, summary_id, issue_date, currency_code):
        NotaDebitoRoot=root
        NotaDebitoRoot.appendChild(self.UBLVersion(ubl_version_id))
        NotaDebitoRoot.appendChild(self.CustomizationID(customization_id))
        NotaDebitoRoot.appendChild(self.SummaryId(summary_id))
        if issue_date:
            NotaDebitoRoot.appendChild(self.IssueDate(issue_date))
        NotaDebitoRoot.appendChild(self.DocumentCurrency(currency_code))
        return NotaDebitoRoot

    #

    def DiscrepancyResponse(self, reference_id, response_code, description):
        DiscrepancyResponse = self.doc.createElement('cac:DiscrepancyResponse')

        ReferenceId = self.doc.createElement('cbc:ReferenceID')
        text = self.doc.createTextNode(reference_id)
        ReferenceId.appendChild(text)
        DiscrepancyResponse.appendChild(ReferenceId)

        ResponseCode = self.doc.createElement('cbc:ResponseCode')
        text = self.doc.createTextNode(response_code)
        ResponseCode.appendChild(text)
        DiscrepancyResponse.appendChild(ResponseCode)

        Description = self.doc.createElement('cbc:Description')
        text = self.doc.createTextNode(description)
        Description.appendChild(text)
        DiscrepancyResponse.appendChild(Description)

        return DiscrepancyResponse

    #

    def BillingReference(self, invoice_id, invoice_type_code):
        BillingReference = self.doc.createElement('cac:BillingReference')
        InvoiceDocument = self.doc.createElement('cac:InvoiceDocumentReference')

        InvoiceId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(invoice_id)
        InvoiceId.appendChild(text)
        InvoiceDocument.appendChild(InvoiceId)

        InvoiceTypeCode = self.doc.createElement('cbc:DocumentTypeCode')
        text = self.doc.createTextNode(invoice_type_code)
        InvoiceTypeCode.appendChild(text)
        InvoiceDocument.appendChild(InvoiceTypeCode)

        BillingReference.appendChild(InvoiceDocument)
        return BillingReference

    # Signature

    def SignatoryParty(self, party_id, party_name):
        SignatoryParty = self.doc.createElement('cac:SignatoryParty')

        PartyIdentification = self.doc.createElement('cac:PartyIdentification')
        PartyId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(party_id)
        PartyId.appendChild(text)
        PartyIdentification.appendChild(PartyId)

        PartyName = self.doc.createElement('cac:PartyName')
        Name = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(party_name)
        Name.appendChild(text)
        PartyName.appendChild(Name)

        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)
        return SignatoryParty

    def Signature(self, signature_id, party_id, party_name, uri):
        Signature = self.doc.createElement('cac:Signature')

        SignatureId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(signature_id)
        SignatureId.appendChild(text)
        Signature.appendChild(SignatureId)

        SignatoryParty = self.SignatoryParty(party_id, party_name)
        Signature.appendChild(SignatoryParty)

        SignatureAttachment = self.doc.createElement('cac:DigitalSignatureAttachment')
        ExternalReference = self.doc.createElement('cac:ExternalReference')
        Uri = self.doc.createElement('cbc:URI')
        text = self.doc.createTextNode(uri)
        Uri.appendChild(text)
        ExternalReference.appendChild(Uri)
        SignatureAttachment.appendChild(ExternalReference)
        Signature.appendChild(SignatureAttachment)

        return Signature

    # Accounting Supplier Party

    def AccountingSupplierParty(self, customer_assigned_id, additional_id, registration_name, address_type_code):
        AccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')

        CustomerAssignedId = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(customer_assigned_id)
        CustomerAssignedId.appendChild(text)

        AdditionalAccountId = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(additional_id)
        AdditionalAccountId.appendChild(text)

        SupplierParty = self.doc.createElement('cac:Party')

        PostalAddress = self.doc.createElement('cac:PostalAddress')
        AddressTypeCode = self.doc.createElement('cbc:AddressTypeCode')
        text = self.doc.createTextNode(address_type_code)
        AddressTypeCode.appendChild(text)
        PostalAddress.appendChild(AddressTypeCode)

        PartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        RegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(registration_name)
        RegistrationName.appendChild(text)
        PartyLegalEntity.appendChild(RegistrationName)

        SupplierParty.appendChild(PostalAddress)
        SupplierParty.appendChild(PartyLegalEntity)
        AccountingSupplierParty.appendChild(CustomerAssignedId)
        AccountingSupplierParty.appendChild(AdditionalAccountId)
        AccountingSupplierParty.appendChild(SupplierParty)
        return AccountingSupplierParty

    # Accounting Customer Party

    def AccountingCustomerParty(self, customer_assigned_id, additional_id, registration_name):
        AccountingSupplierParty = self.doc.createElement('cac:AccountingCustomerParty')

        CustomerAssignedId = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(customer_assigned_id)
        CustomerAssignedId.appendChild(text)

        AdditionalAccountId = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(additional_id)
        AdditionalAccountId.appendChild(text)

        SupplierParty = self.doc.createElement('cac:Party')

        PartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        RegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(registration_name)
        RegistrationName.appendChild(text)
        PartyLegalEntity.appendChild(RegistrationName)

        SupplierParty.appendChild(PartyLegalEntity)
        AccountingSupplierParty.appendChild(CustomerAssignedId)
        AccountingSupplierParty.appendChild(AdditionalAccountId)
        AccountingSupplierParty.appendChild(SupplierParty)
        return AccountingSupplierParty

    # Requested Monetary Total

    def RequestedMonetaryTotal(self, payable_amount):
        RequestedMonetaryTotal = self.doc.createElement('cac:RequestedMonetaryTotal')

        PayableAmount = self.doc.createElement('cbc:PayableAmount')
        PayableAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(payable_amount)
        PayableAmount.appendChild(text)

        RequestedMonetaryTotal.appendChild(PayableAmount)
        return RequestedMonetaryTotal

    # Debit Note Line

    def LinePricingReference(self, price_amount, price_type_code):
        PricingReference = self.doc.createElement('cac:PricingReference')

        AlternativeConditionPrice = self.doc.createElement('cac:AlternativeConditionPrice')
        PriceAmount = self.doc.createElement('cbc:PriceAmount')
        PriceAmount.setAttribute("currencyID", "PEN")
        text = self.doc.createTextNode(price_amount)
        PriceAmount.appendChild(text)

        PriceTypeCode = self.doc.createElement('cbc:PriceTypeCode')
        text = self.doc.createTextNode(price_type_code)
        PriceTypeCode.appendChild(text)

        AlternativeConditionPrice.appendChild(PriceAmount)
        AlternativeConditionPrice.appendChild(PriceTypeCode)

        PricingReference.appendChild(AlternativeConditionPrice)
        return PricingReference

    def LineTaxTotal(self, tax_amount, tax_amount_subtotal, tax_exemption_code, tax_id, tax_name,
                     tax_type_code):
        TaxTotal = self.doc.createElement('cac:TaxTotal')

        TaxAmount = self.doc.createElement('cbc:TaxAmount')
        TaxAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(tax_amount)
        TaxAmount.appendChild(text)

        TaxSubtotal = self.doc.createElement('cac:TaxSubtotal')
        TaxAmountSubtotal = self.doc.createElement('cbc:TaxAmount')
        TaxAmountSubtotal.setAttribute('currencyID', "PEN")
        text = self.doc.createTextNode(tax_amount_subtotal)
        TaxAmountSubtotal.appendChild(text)

        TaxCategory = self.doc.createElement('cac:TaxCategory')
        TaxExemptionCode = self.doc.createElement('cbc:TaxExemptionReasonCode')
        text = self.doc.createTextNode(tax_exemption_code)
        TaxExemptionCode.appendChild(text)

        TaxScheme = self.doc.createElement('cac:TaxScheme')
        TaxId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(tax_id)
        TaxId.appendChild(text)
        TaxName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(tax_name)
        TaxName.appendChild(text)
        TaxTypeCode = self.doc.createElement('cbc:TaxTypeCode')
        text = self.doc.createTextNode(tax_type_code)
        TaxTypeCode.appendChild(text)
        TaxScheme.appendChild(TaxId)
        TaxScheme.appendChild(TaxName)
        TaxScheme.appendChild(TaxTypeCode)
        TaxCategory.appendChild(TaxExemptionCode)
        TaxCategory.appendChild(TaxScheme)
        TaxSubtotal.appendChild(TaxAmountSubtotal)
        TaxSubtotal.appendChild(TaxCategory)

        TaxTotal.appendChild(TaxAmount)
        TaxTotal.appendChild(TaxSubtotal)
        return TaxTotal

    def Item(self, description, sellers_id):
        Item = self.doc.createElement('cac:Item')

        Description = self.doc.createElement('cbc:Description')
        text = self.doc.createTextNode(description)
        Description.appendChild(text)

        SellersIdentification = self.doc.createElement('cac:SellersItemIdentification')
        SellersId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(sellers_id)
        SellersId.appendChild(text)
        SellersIdentification.appendChild(SellersId)

        Item.appendChild(Description)
        Item.appendChild(SellersIdentification)
        return Item

    def DebitNoteLine(self, line_id, line_debited_quantity, line_extension_amount, price_amount, price_type_code,
                      tax_exemption_code, tax_amount, description, sellers_id, line_price_amount, array_tax_totals,currency_id,unit_code):
        DebitNoteLine = self.doc.createElement('cac:DebitNoteLine')

        LineId = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(line_id)
        LineId.appendChild(text)

        DebitedQuantity = self.doc.createElement('cbc:DebitedQuantity')
        DebitedQuantity.setAttribute("unitCode", unit_code)
        text = self.doc.createTextNode(line_debited_quantity)
        DebitedQuantity.appendChild(text)

        LineExtensionAmount = self.doc.createElement('cbc:LineExtensionAmount')
        LineExtensionAmount.setAttribute('currencyID', currency_id)
        text = self.doc.createTextNode(line_extension_amount)
        LineExtensionAmount.appendChild(text)

        PricingReference = self.LinePricingReference(price_amount, price_type_code)

        DebitNoteLine.appendChild(LineId)
        DebitNoteLine.appendChild(DebitedQuantity)
        DebitNoteLine.appendChild(LineExtensionAmount)
        DebitNoteLine.appendChild(PricingReference)

        for tax in array_tax_totals:
            TaxTotal = self.LineTaxTotal(tax["TaxAmount"], tax["TaxAmount"], tax_exemption_code, tax["tributo_codigo"],
                                              tax["tributo_nombre"], tax["tributo_tipo_codigo"])
            DebitNoteLine.appendChild(TaxTotal)

        Item = self.Item(description, sellers_id)

        DebitNoteLine.appendChild(Item)

        Price = self.doc.createElement('cac:Price')
        PriceAmount = self.doc.createElement('cbc:PriceAmount')
        PriceAmount.setAttribute('currencyID', 'PEN')
        text = self.doc.createTextNode(line_price_amount)
        PriceAmount.appendChild(text)
        Price.appendChild(PriceAmount)

        DebitNoteLine.appendChild(Price)
        return DebitNoteLine


    def AdditionalMonetaryTotal(self,currencyID,gravado,exonerado,inafecto,gratuito,total_descuento):
        extUBLExtensions = self.doc.createElement("ext:UBLExtensions")
        extUBLExtension = self.doc.createElement("ext:UBLExtension")
        extExtensionContent = self.doc.createElement("ext:ExtensionContent")
        sacAdditionalInformation = self.doc.createElement("sac:AdditionalInformation")

        #OPERACIONES GRAVADAS
        sacAdditionalMonetaryTotal_gravado = self.doc.createElement("sac:AdditionalMonetaryTotal")

        cbcID=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode("1001")
        cbcID.appendChild(text)

        cbcPayableAmount=self.doc.createElement("cbc:PayableAmount")
        cbcPayableAmount.setAttribute("currencyID",currencyID)
        text=self.doc.createTextNode(str(gravado))
        cbcPayableAmount.appendChild(text)

        sacAdditionalMonetaryTotal_gravado.appendChild(cbcID)
        sacAdditionalMonetaryTotal_gravado.appendChild(cbcPayableAmount)



        #OPERACIONES EXONERADAS
        sacAdditionalMonetaryTotal_exonerado = self.doc.createElement("sac:AdditionalMonetaryTotal")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode("1003")
        cbcID.appendChild(text)

        cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
        cbcPayableAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(exonerado))
        cbcPayableAmount.appendChild(text)

        sacAdditionalMonetaryTotal_exonerado.appendChild(cbcID)
        sacAdditionalMonetaryTotal_exonerado.appendChild(cbcPayableAmount)

        #OPERACIONES INAFECTAS
        sacAdditionalMonetaryTotal_inafecto = self.doc.createElement("sac:AdditionalMonetaryTotal")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode("1002")
        cbcID.appendChild(text)

        cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
        cbcPayableAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(inafecto))
        cbcPayableAmount.appendChild(text)

        sacAdditionalMonetaryTotal_inafecto.appendChild(cbcID)
        sacAdditionalMonetaryTotal_inafecto.appendChild(cbcPayableAmount)



        sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_gravado)
        sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_exonerado)
        sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_inafecto)

        # sac:AdditionalProperty 1002 TRANSFERENCIA GRATUITA DE UN BIOEN O SERVICIO PRESTADO GRATUITAMENTE
        # OBLIGATORIO:
        """
            Aplicable solo en el caso que todas las operaciones (lineas o items) comprendidas en
            la factura electrOnica sean gratuitas.
            En el elemento cbc:ID se debe consignar el cOdigo 1002 (segun Catalogo No. 15).
        """
        if gratuito>0 and gravado==0 and exonerado==0 and inafecto==0  and total_descuento==0 :
            sacAdditionalProperty=self.doc.createElement("sac:AdditionalProperty")
            cbcID=self.doc.createElement("cbc:ID")
            text=self.doc.createTextNode("1002")
            cbcID.appendChild(text)
            cbcValue=self.doc.createElement("cbc:Value")
            text=self.doc.createTextNode("TRANSFERENCIA GRATUITA DE UN BIEN Y/O SERVICIO PRESTADO GRATUITAMENTE")
            cbcValue.appendChild(text)
            sacAdditionalProperty.appendChild(cbcID)
            sacAdditionalProperty.appendChild(cbcValue)
            sacAdditionalInformation.appendChild(sacAdditionalProperty)

        extExtensionContent.appendChild(sacAdditionalInformation)
        extUBLExtension.appendChild(extExtensionContent)

        extUBLExtensions.appendChild(extUBLExtension)

        return extUBLExtensions

    def firma(self,id):
        UBLExtension=self.doc.createElement("ext:UBLExtension")
        ExtensionContent=self.doc.createElement("ext:ExtensionContent")
        Signature=self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id",id)
        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)
        return UBLExtension


    """
    DatosProveedor:Datos del Emisor del documento

    Parametros:
       num_doc_ident: Numero de Documento de Identidad
       tipo_doc_ident: Tipo de Documento de Identificacion
       nombre_comercial: Nombre del Comercio
       codigo_ubigeo: Codigo del ubigeo del Comercio
       nombre_direccion_full:  Direccion Completa y Detallada
       nombre_direccion_division: Urbanizacion o Zona
       nombre_departamento: Nombre del Departamento
       nombre_distrito: Nombre de Distrito
       nombre_proveedor: Nombre de Proveedor
       codigo_pais: Codigo del pais
    devuelve:
    	XML cac:AccountingSupplierParty  con datos del Emisor
    """

    def cacAccountingSupplierParty(self,num_doc_ident,
                       tipo_doc_ident,
                       nombre_comercial,
                       codigo_ubigeo,
                       nombre_direccion_full,
                       nombre_direccion_division,
                       nombre_departamento,
                       nombre_provincia,
                       nombre_distrito,
                       nombre_proveedor,
                       codigo_pais):
        cacAccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')

        # Numero de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacAccountingSupplierParty.appendChild(cbcCustomerAssignedAccountID)

        # tipo de documento de identidad
        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(tipo_doc_ident)
        cbcAdditionalAccountID.appendChild(text)
        cacAccountingSupplierParty.appendChild(cbcAdditionalAccountID)

        cacParty = self.doc.createElement('cac:Party')
        cacAccountingSupplierParty.appendChild(cacParty)

        cacPartyName = self.doc.createElement('cac:PartyName')
        cacParty.appendChild(cacPartyName)

        # Nombre Comercial
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(str(nombre_comercial))
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)

        # Domicilio Fiscal
        cacPostalAddress = self.doc.createElement('cac:PostalAddress')
        cacParty.appendChild(cacPostalAddress)

        # Codigo de ubigeo
        if codigo_ubigeo:
            cbcID = self.doc.createElement('cbc:ID')
            text = self.doc.createTextNode(str(codigo_ubigeo))
            cbcID.appendChild(text)
            cacPostalAddress.appendChild(cbcID)

        # Direccion Completa y Detallada
        cbcStreetName = self.doc.createElement('cbc:StreetName')
        text = self.doc.createTextNode(nombre_direccion_full)
        cbcStreetName.appendChild(text)
        cacPostalAddress.appendChild(cbcStreetName)

        # Urbanizacion o zona
        if nombre_direccion_division:
            cbcCitySubdivisionName = self.doc.createElement('cbc:CitySubdivisionName')
            text = self.doc.createTextNode(nombre_direccion_division)
            cbcCitySubdivisionName.appendChild(text)
            cacPostalAddress.appendChild(cbcCitySubdivisionName)

        # Nombre de Ciudad
        cbcCityName = self.doc.createElement('cbc:CityName')
        text = self.doc.createTextNode(str(nombre_departamento))
        cbcCityName.appendChild(text)
        cacPostalAddress.appendChild(cbcCityName)

        # Nombre de Provincia
        cbcCountrySubentity = self.doc.createElement('cbc:CountrySubentity')
        text = self.doc.createTextNode(str(nombre_provincia))
        cbcCountrySubentity.appendChild(text)
        cacPostalAddress.appendChild(cbcCountrySubentity)

        # Nombre de Distrito
        cbcDistrict = self.doc.createElement('cbc:District')
        text = self.doc.createTextNode(str(nombre_distrito))
        cbcDistrict.appendChild(text)
        cacPostalAddress.appendChild(cbcDistrict)

        # Codigo de pais
        cacCountry = self.doc.createElement('cac:Country')
        cacPostalAddress.appendChild(cacCountry)
        cbcIdentificationCode = self.doc.createElement('cbc:IdentificationCode')
        text = self.doc.createTextNode(str(codigo_pais))
        cbcIdentificationCode.appendChild(text)
        cacCountry.appendChild(cbcIdentificationCode)

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(str(nombre_proveedor))
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacAccountingSupplierParty



    """
    DatosCliente: Datos del Adquiriente o Usuario

    Parametros:
    	num_doc_identidad: Numero de documento de identidad
    	tipo_doc_identidad: Tipo de Documento de identidad
    	nombre_cliente:Apellidos y nombres o denominacion o razon social segun RUC
    devuelve:
    	XML cac:AccountingCustomerParty  con datos del Cliente
    """


    def cacAccountCustomerParty(self,num_doc_identidad, tipo_doc_identidad, nombre_cliente):
        cacAccountingCustomerParty = self.doc.createElement('cac:AccountingCustomerParty')

        # Numero de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(num_doc_identidad)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacAccountingCustomerParty.appendChild(cbcCustomerAssignedAccountID)

        # Tipo de Documento de Identidad
        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(tipo_doc_identidad)
        cbcAdditionalAccountID.appendChild(text)
        cacAccountingCustomerParty.appendChild(cbcAdditionalAccountID)

        # Apellidos y nombres o denominacion o razon social segun RUC
        cacParty = self.doc.createElement('cac:Party')
        cacAccountingCustomerParty.appendChild(cacParty)
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(nombre_cliente)
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacAccountingCustomerParty


    def TaxTotal(self,currencyID,TaxAmount,tributo_id,tributo_nombre,tributo_codigo):
        cacTaxTotal=self.doc.createElement("cac:TaxTotal")

        cbcTaxAmount=self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID",currencyID)
        text=self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)


        cacTaxSubtotal=self.doc.createElement("cac:TaxSubtotal")

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory=self.doc.createElement("cac:TaxCategory")
        cacTaxScheme=self.doc.createElement("cac:TaxScheme")
        cbcID=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(str(tributo_id))
        cbcID.appendChild(text)

        cbcName=self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(str(tributo_nombre))
        cbcName.appendChild(text)

        cbcTaxTypeCode = self.doc.createElement("cbc:TaxTypeCode")
        text = self.doc.createTextNode(str(tributo_codigo))
        cbcTaxTypeCode.appendChild(text)

        cacTaxScheme.appendChild(cbcID)
        cacTaxScheme.appendChild(cbcName)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cacTaxScheme)

        cacTaxSubtotal.appendChild(cacTaxCategory)
        cacTaxTotal.appendChild(cacTaxSubtotal)

        return cacTaxTotal


    def LegalMonetaryTotal(self,MontoTotal,currency_id):
        LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")
        PayableAmount = self.doc.createElement("cbc:PayableAmount")
        PayableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(MontoTotal))
        PayableAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(PayableAmount)
        return LegalMonetaryTotal


    """
        cac:TaxTotal                                        1..n    Informacion acerca del importe total de un tipo particular de impuesto. Una repeticion por IGV, ISC
            cbc:TaxAmount/@currencyID                       1       Importe total de un tributo para este item
            cac:TaxSubtotal
                cbc:TaxAmount/@currencyID                   1       Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
                cac:TaxCategory/cbc:TaxExemptionReasonCode  1       Afectacion al IGV (catalogo No 7)
                cac:TaxCategory/cbc:TierRange               1       Sistema de ISC (catalogo No 8)
                cac:TaxCategory/cac:TaxScheme/cbc:ID        1       Identificaion del tributo segun el (catalogo No 5)
                cac:TaxCategory/cac:TaxScheme/cbc:Name      1       Nombre del Tributo (IGV, ISC)
    """

    def cacTaxTotal(self,tax):
        currencyID=tax["currencyID"]
        TaxAmount=tax["TaxAmount"]
        TaxExemptionReasonCode=tax["TaxExemptionReasonCode"]
        TierRange=tax["TierRange"]
        tributo_codigo=tax["tributo_codigo"]
        tributo_nombre=tax["tributo_nombre"]
        tributo_tipo_codigo=tax["tributo_tipo_codigo"]

        # Importe total de un tributo para este item
        cacTaxTotal = self.doc.createElement('cac:TaxTotal')

        # Monto de IGV de la linea
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)

        cacTaxSubtotal = self.doc.createElement('cac:TaxSubtotal')

        # Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory = self.doc.createElement('cac:TaxCategory')

        if tributo_codigo=="1000":
            # Afectacion del IGV  (Catalogo No. 07)
            cbcTaxExemptionReasonCode = self.doc.createElement('cbc:TaxExemptionReasonCode')
            text = self.doc.createTextNode(TaxExemptionReasonCode)
            cbcTaxExemptionReasonCode.appendChild(text)
            cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
        if tributo_codigo=="2000":
            #Sistema de ISC (Catalogo No 08)
            cbcTierRange=self.doc.createElement("cbc:TierRange")
            text=self.doc.createTextNode(TierRange)
            cbcTierRange.appendChild(text)
            cacTaxCategory.appendChild(cbcTierRange)

        # Tipo de Tributo (Catalogo No. 05)
        """
            codigo  Descripcion                              Nombre del Tipo de Codigo
            1000 	IGV    IMPUESTO GENERAL A LAS VENTAS     VAT
            2000 	ISC    IMPUESTO SELECTIVO AL CONSUMO     EXC
            9999 	OTROS CONCEPTOS DE PAGO				     OTH
        """
        cacTaxScheme = self.doc.createElement('cac:TaxScheme')

        # Tipo de Tributo:Codigo
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(tributo_codigo)
        cbcID.appendChild(text)
        cacTaxScheme.appendChild(cbcID)

        # Tipo de Tributo: Nombre
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(tributo_nombre)
        cbcName.appendChild(text)

        cacTaxScheme.appendChild(cbcName)

        # Tipo de Tributo: Tipo de Codigo
        cbcTaxTypeCode = self.doc.createElement('cbc:TaxTypeCode')
        text = self.doc.createTextNode(tributo_tipo_codigo)
        cbcTaxTypeCode.appendChild(text)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cacTaxScheme)
        cacTaxSubtotal.appendChild(cacTaxCategory)
        cacTaxTotal.appendChild(cacTaxSubtotal)

        return cacTaxTotal
