from xml.dom import minidom


class Factura:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement("Invoice")
        self.doc.appendChild(root)
        root.setAttribute(
            "xmlns", "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
        )
        root.setAttribute(
            "xmlns:cac",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        )
        root.setAttribute(
            "xmlns:cbc",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        )
        root.setAttribute("xmlns:ccts", "urn:un:unece:uncefact:documentation:2")
        root.setAttribute("xmlns:ds", "http://www.w3.org/2000/09/xmldsig#")
        root.setAttribute(
            "xmlns:ext",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        )
        root.setAttribute(
            "xmlns:qdt",
            "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
        )
        root.setAttribute(
            "xmlns:udt",
            "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
        )
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

        return root

    def UBLExtensions(self):
        extUBLExtensions = self.doc.createElement("ext:UBLExtensions")
        extUBLExtensions.appendChild(self.firma(id="placeholder"))

        return extUBLExtensions

    def firma(self, id):
        UBLExtension = self.doc.createElement("ext:UBLExtension")
        ExtensionContent = self.doc.createElement("ext:ExtensionContent")
        Signature = self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id", id)
        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)

        return UBLExtension

    def UBLVersion(self, id):
        UBLVersion = self.doc.createElement("cbc:UBLVersionID")
        text = self.doc.createTextNode(id)
        UBLVersion.appendChild(text)
        return UBLVersion

    def CustomizationID(self, id):
        cbcCustomizationID = self.doc.createElement("cbc:CustomizationID")
        text = self.doc.createTextNode(str(id))
        cbcCustomizationID.appendChild(text)
        return cbcCustomizationID

    def ID(self, id):
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        cbcID.appendChild(text)
        return cbcID

    def issueDate(self, fecha):
        cbcIssueDate = self.doc.createElement("cbc:IssueDate")
        text = self.doc.createTextNode(fecha)
        cbcIssueDate.appendChild(text)
        return cbcIssueDate

    def issueTime(self, hora):
        cbcIssueDate = self.doc.createElement("cbc:IssueTime")
        text = self.doc.createTextNode(hora)
        cbcIssueDate.appendChild(text)
        return cbcIssueDate

    def invoiceTypeCode(self, invoicetypecode, operacion):
        cbcInvoiceTypeCode = self.doc.createElement("cbc:InvoiceTypeCode")
        cbcInvoiceTypeCode.setAttribute("listID", str(operacion))
        text = self.doc.createTextNode(str(invoicetypecode))
        cbcInvoiceTypeCode.appendChild(text)
        return cbcInvoiceTypeCode

    def documentCurrencyCode(self, documentcurrencycode):
        cbcDocumentCurrencyCode = self.doc.createElement("cbc:DocumentCurrencyCode")
        text = self.doc.createTextNode(documentcurrencycode)
        cbcDocumentCurrencyCode.appendChild(text)
        return cbcDocumentCurrencyCode

    def Signature(self, Id, ruc, razon_social, uri):
        Signature = self.doc.createElement("cac:Signature")
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(Id)
        ID.appendChild(text)
        Signature.appendChild(ID)

        SignatoryParty = self.doc.createElement("cac:SignatoryParty")
        PartyIdentification = self.doc.createElement("cac:PartyIdentification")
        RUC = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ruc)
        RUC.appendChild(text)
        PartyIdentification.appendChild(RUC)
        PartyName = self.doc.createElement("cac:PartyName")
        Name = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(razon_social)
        Name.appendChild(text)
        PartyName.appendChild(Name)
        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)

        Signature.appendChild(SignatoryParty)

        DigitalSignatureAttachment = self.doc.createElement(
            "cac:DigitalSignatureAttachment"
        )
        ExternalReference = self.doc.createElement("cac:ExternalReference")
        URI = self.doc.createElement("cbc:URI")
        text = self.doc.createTextNode(uri)
        URI.appendChild(text)
        ExternalReference.appendChild(URI)
        DigitalSignatureAttachment.appendChild(ExternalReference)

        Signature.appendChild(DigitalSignatureAttachment)

        return Signature

    def cacAdditionalDocumentReference(self, documento, num_doc_ident, tipo_doc_ident):
        cacAdditionalDocumentReference = self.doc.createElement(
            "cac:AdditionalDocumentReference"
        )
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(documento)
        cbcID.appendChild(text)

        cbcDocumentTypeCode = self.doc.createElement("cbc:DocumentTypeCode")
        text = self.doc.createTextNode("02")
        cbcDocumentTypeCode.appendChild(text)

        cbcDocumentStatusCode = self.doc.createElement("cbc:DocumentStatusCode")
        text = self.doc.createTextNode(documento)
        cbcDocumentStatusCode.appendChild(text)

        cacIssuerParty = self.doc.createElement("cac:IssuerParty")
        cacPartyIdentification = self.doc.createElement("cac:PartyIdentification")
        cbcIDip = self.doc.createElement("cbc:ID")
        cbcIDip.setAttribute("schemeID", tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcIDip.appendChild(text)

        cacPartyIdentification.appendChild(cbcIDip)

        cacIssuerParty.appendChild(cacPartyIdentification)

        cacAdditionalDocumentReference.appendChild(cbcID)
        cacAdditionalDocumentReference.appendChild(cbcDocumentTypeCode)
        cacAdditionalDocumentReference.appendChild(cbcDocumentStatusCode)
        cacAdditionalDocumentReference.appendChild(cacIssuerParty)

        return cacAdditionalDocumentReference

    def cacPrepaidPayment(self, currency, monto, documento):
        cacPrepaidPayment = self.doc.createElement("cac:PrepaidPayment")
        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID", "02")
        text = self.doc.createTextNode(documento)
        cbcID.appendChild(text)

        cbcPaidAmount = self.doc.createElement("cbc:PaidAmount")
        cbcPaidAmount.setAttribute("currencyID", currency)
        text = self.doc.createTextNode(str(monto))
        cbcPaidAmount.appendChild(text)

        cacPrepaidPayment.appendChild(cbcID)
        cacPrepaidPayment.appendChild(cbcPaidAmount)

        return cacPrepaidPayment

    #########################################################################
    #########################################################################
    ## /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID
    ## /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID@schemeID (Tipo de documento de identidad)
    ## /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName
    ## /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:AddressTypeCode
    #########################################################################
    #########################################################################
    def cacAccountingSupplierParty(
        self,
        num_doc_ident,
        tipo_doc_ident,
        nombre_comercial,
        codigo_ubigeo,
        nombre_direccion_full,
        nombre_direccion_division,
        nombre_departamento,
        nombre_provincia,
        nombre_distrito,
        nombre_proveedor,
        codigo_pais,
    ):
        cacAccountingSupplierParty = self.doc.createElement("cac:AccountingSupplierParty")

        cacParty = self.doc.createElement("cac:Party")

        cacPartyIdentification = self.doc.createElement("cac:PartyIdentification")
        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID", "6")
        text = self.doc.createTextNode(num_doc_ident)
        cbcID.appendChild(text)
        cacPartyIdentification.appendChild(cbcID)

        cacPartyLegalEntity = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName")
        text = self.doc.createTextNode(nombre_proveedor)
        cbcRegistrationName.appendChild(text)

        cacRegistrationAddress = self.doc.createElement("cac:RegistrationAddress")
        cbcAddressTypeCode = self.doc.createElement("cbc:AddressTypeCode")
        text = self.doc.createTextNode("0000")
        cbcAddressTypeCode.appendChild(text)
        cacRegistrationAddress.appendChild(cbcAddressTypeCode)

        cacPartyLegalEntity.appendChild(cbcRegistrationName)
        cacPartyLegalEntity.appendChild(cacRegistrationAddress)

        cacParty.appendChild(cacPartyIdentification)
        cacParty.appendChild(cacPartyLegalEntity)

        cacAccountingSupplierParty.appendChild(cacParty)

        return cacAccountingSupplierParty

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    #########################################################################
    #########################################################################
    ## /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID (# de documento)
    ## /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID@schemeID (Tipo de documento de identidad)
    ## /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName
    #########################################################################
    #########################################################################
    def cacAccountingCustomerParty(
        self, num_doc_identidad, tipo_doc_identidad, nombre_cliente
    ):
        cacAccountingCustomerParty = self.doc.createElement("cac:AccountingCustomerParty")

        cacParty = self.doc.createElement("cac:Party")

        cacPartyIdentification = self.doc.createElement("cac:PartyIdentification")
        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID", tipo_doc_identidad)
        text = self.doc.createTextNode(num_doc_identidad)
        cbcID.appendChild(text)
        cacPartyIdentification.appendChild(cbcID)

        cacPartyLegalEntity = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName")
        text = self.doc.createTextNode(nombre_cliente)
        cbcRegistrationName.appendChild(text)

        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        cacParty.appendChild(cacPartyIdentification)
        cacParty.appendChild(cacPartyLegalEntity)

        cacAccountingCustomerParty.appendChild(cacParty)

        return cacAccountingCustomerParty

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    ## /Invoice/cac:TaxTotal/cbc:TaxAmount
    ## /Invoice/cac:TaxTotal/cbc:TaxAmount@currencyID
    ##### (Total valor de venta operaciones gravadas)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount@currencyID
    ##### (Total Importe de IGV o IVAP, segun corresponda)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount@currencyID
    ##### (Codigo de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID
    ##### (Nombre de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name
    ##### (Codigo internacional de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaImporte de IGV o IVAP, segun corresponda)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount@currencyID
    ##### (Codigo de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID
    ##### (Nombre de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name
    ##### (Codigo internacional de tributo)
    ## /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode
    #########################################################################
    #########################################################################
    # def cacTaxTotal(self, currency_id, taxtotal, gravadas, igv, tributo_code, tributo_name, tributo_id):
    def cacTaxTotal(self, currency_id, taxtotal, gratuitas, gravado):
        cacTaxTotal = self.doc.createElement("cac:TaxTotal")

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(taxtotal))
        cbcTaxAmount.appendChild(text)

        cacTaxSubtotalgravado = self.doc.createElement("cac:TaxSubtotal")
        cbcTaxableAmountgravado = self.doc.createElement("cbc:TaxableAmount")
        cbcTaxableAmountgravado.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(gravado))
        cbcTaxableAmountgravado.appendChild(text)

        _cbcTaxAmountgravado = self.doc.createElement("cbc:TaxAmount")
        _cbcTaxAmountgravado.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(taxtotal))
        _cbcTaxAmountgravado.appendChild(text)

        cacTaxCategorygravado = self.doc.createElement("cac:TaxCategory")
        cacTaxSchemegravado = self.doc.createElement("cac:TaxScheme")
        cbcIDgravado = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode("1000")
        cbcIDgravado.appendChild(text)
        cbcNamegravado = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode("IGV")
        cbcNamegravado.appendChild(text)
        cbcTaxTypeCodegravado = self.doc.createElement("cbc:TaxTypeCode")
        text = self.doc.createTextNode("VAT")
        cbcTaxTypeCodegravado.appendChild(text)

        cacTaxSubtotal = self.doc.createElement("cac:TaxSubtotal")
        cbcTaxableAmount = self.doc.createElement("cbc:TaxableAmount")
        cbcTaxableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(gratuitas))
        cbcTaxableAmount.appendChild(text)

        _cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        _cbcTaxAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode("0.0")
        _cbcTaxAmount.appendChild(text)

        cacTaxCategory = self.doc.createElement("cac:TaxCategory")
        cacTaxScheme = self.doc.createElement("cac:TaxScheme")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode("9996")
        cbcID.appendChild(text)
        cbcName = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode("GRA")
        cbcName.appendChild(text)
        cbcTaxTypeCode = self.doc.createElement("cbc:TaxTypeCode")
        text = self.doc.createTextNode("FRE")
        cbcTaxTypeCode.appendChild(text)

        cacTaxScheme.appendChild(cbcID)
        cacTaxScheme.appendChild(cbcName)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cacTaxScheme)

        cacTaxSubtotal.appendChild(cbcTaxableAmount)
        cacTaxSubtotal.appendChild(_cbcTaxAmount)
        cacTaxSubtotal.appendChild(cacTaxCategory)

        cacTaxSchemegravado.appendChild(cbcIDgravado)
        cacTaxSchemegravado.appendChild(cbcNamegravado)
        cacTaxSchemegravado.appendChild(cbcTaxTypeCodegravado)

        cacTaxCategorygravado.appendChild(cacTaxSchemegravado)

        cacTaxSubtotalgravado.appendChild(cbcTaxableAmountgravado)
        cacTaxSubtotalgravado.appendChild(_cbcTaxAmountgravado)
        cacTaxSubtotalgravado.appendChild(cacTaxCategorygravado)

        cacTaxTotal.appendChild(cbcTaxAmount)

        if gratuitas > 0:
            cacTaxTotal.appendChild(cacTaxSubtotal)
        else:
            cacTaxTotal.appendChild(cacTaxSubtotalgravado)

        return cacTaxTotal

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    #########################################################################
    #########################################################################
    ## /Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount
    #########################################################################
    #########################################################################
    def cacLegalMonetaryTotal(self, total, prepaid, currency_id):
        cacLegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")

        cbcPrepaidAmount = self.doc.createElement("cbc:PrepaidAmount")
        cbcPrepaidAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(prepaid))
        cbcPrepaidAmount.appendChild(text)

        cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
        cbcPayableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(total))
        cbcPayableAmount.appendChild(text)

        cacLegalMonetaryTotal.appendChild(cbcPrepaidAmount)
        cacLegalMonetaryTotal.appendChild(cbcPayableAmount)

        return cacLegalMonetaryTotal

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    #########################################################################
    #########################################################################
    ## /Invoice/cac:InvoiceLine/cbc:ID
    ## /Invoice/cac:InvoiceLine/cbc:LineExtensionAmount
    ## /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity
    ## /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity@unitCode
    ## /Invoice/cac:InvoiceLine/cac:Item/cbc:Description
    ## /Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount
    ## /Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount@currencyID
    ##### (Valor)
    ## /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount
    ## /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount@currencyID
    ##### (Codigo de precio)
    ## /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode
    ##### (Monto total de impuestos por linea)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount@currencyID
    ##### (Monto Base)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount@currencyID
    ##### (Monto de IGV/IVAP de la linea)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount@currencyID
    ##### (Tasa del IGV o  Tasa del IVAP)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent
    ##### (Afectacion al IGV o IVAP cuando corresponda)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode
    ##### (Codigo de tributo por linea)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID
    ##### (Nombre de tributo)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name
    ##### (Codigo internacional de tributo)
    ## /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode
    #########################################################################
    #########################################################################
    def cacInvoiceLine(
        self,
        operacionTipo,
        idline,
        muestra,
        valor,
        currency_id,
        unitcode,
        quantity,
        description,
        price,
        taxtotal,
        afectacion,
        taxcode,
        taxname,
        taxtype,
    ):
        # Definimos variables a usar en el esquema
        if operacionTipo in ("0101", "0401"):
            if afectacion == "10":
                taxcode = "1000"
                taxname = "IGV"
                taxtype = "VAT"
                pricetype = "01"
                priceamount = price

            elif afectacion in (
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "21",
                "31",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
            ):
                taxcode = "9996"
                taxname = "GRA"
                taxtype = "FRE"
                pricetype = "02"
                priceamount = "0.0"

            elif afectacion == "20":
                taxcode = "9997"
                taxname = "EXO"
                taxtype = "VAT"
                pricetype = "01"
                priceamount = price

            elif afectacion == "30":
                taxcode = "9998"
                taxname = "INA"
                taxtype = "FRE"
                pricetype = "01"
                priceamount = price

        elif operacionTipo == "0200":
            if muestra == True:
                taxcode = "9996"
                taxname = "GRA"
                taxtype = "FRE"
                pricetype = "02"
                priceamount = "0.0"
            else:
                taxcode = "9995"
                taxname = "EXP"
                taxtype = "FRE"
                pricetype = "01"
                priceamount = price

        cacInvoiceLine = self.doc.createElement("cac:InvoiceLine")

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(idline))
        cbcID.appendChild(text)

        cbcInvoicedQuantity = self.doc.createElement("cbc:InvoicedQuantity")
        cbcInvoicedQuantity.setAttribute("unitCode", unitcode)
        text = self.doc.createTextNode(quantity)
        cbcInvoicedQuantity.appendChild(text)

        cbcLineExtensionAmount = self.doc.createElement("cbc:LineExtensionAmount")
        cbcLineExtensionAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(valor)
        cbcLineExtensionAmount.appendChild(text)

        cacItem = self.doc.createElement("cac:Item")
        cbcDescription = self.doc.createElement("cbc:Description")
        text = self.doc.createTextNode(description)
        cbcDescription.appendChild(text)

        # cacCommodityClassification = self.doc.createElement('cac:CommodityClassification')
        # cbcItemClassificationCode = self.doc.createElement('cbc:ItemClassificationCode')
        # text = self.doc.createTextNode(str('55101509'))
        # cbcItemClassificationCode.appendChild(text)
        # cacCommodityClassification.appendChild(cbcItemClassificationCode)

        cacItem.appendChild(cbcDescription)
        # cacItem.appendChild(cacCommodityClassification)

        cacPrice = self.doc.createElement("cac:Price")
        cbcPriceAmount = self.doc.createElement("cbc:PriceAmount")
        cbcPriceAmount.setAttribute("currencyID", currency_id)
        # text = self.doc.createTextNode(str(price))
        text = self.doc.createTextNode(priceamount)
        cbcPriceAmount.appendChild(text)
        cacPrice.appendChild(cbcPriceAmount)

        cacPricingReference = self.doc.createElement("cac:PricingReference")
        cacAlternativeConditionPrice = self.doc.createElement(
            "cac:AlternativeConditionPrice"
        )
        cbcPriceAmount = self.doc.createElement("cbc:PriceAmount")
        cbcPriceAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(price)
        cbcPriceAmount.appendChild(text)
        cbcPriceTypeCode = self.doc.createElement("cbc:PriceTypeCode")
        text = self.doc.createTextNode(pricetype)
        cbcPriceTypeCode.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceAmount)
        cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)
        cacPricingReference.appendChild(cacAlternativeConditionPrice)

        cacTaxTotal = self.doc.createElement("cac:TaxTotal")
        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(taxtotal))
        cbcTaxAmount.appendChild(text)

        cacTaxSubtotal = self.doc.createElement("cac:TaxSubtotal")
        cbcTaxableAmount = self.doc.createElement("cbc:TaxableAmount")
        cbcTaxableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(valor))
        cbcTaxableAmount.appendChild(text)

        _cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        _cbcTaxAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(taxtotal))
        _cbcTaxAmount.appendChild(text)

        cacTaxCategory = self.doc.createElement("cac:TaxCategory")
        cbcPercent = self.doc.createElement("cbc:Percent")
        text = self.doc.createTextNode("18.00")
        cbcPercent.appendChild(text)

        cbcTaxExemptionReasonCode = self.doc.createElement("cbc:TaxExemptionReasonCode")
        text = self.doc.createTextNode(str(afectacion))
        cbcTaxExemptionReasonCode.appendChild(text)

        cacTaxScheme = self.doc.createElement("cac:TaxScheme")

        _cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(taxcode))
        _cbcID.appendChild(text)

        cbcName = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(str(taxname))
        cbcName.appendChild(text)

        cbcTaxTypeCode = self.doc.createElement("cbc:TaxTypeCode")
        text = self.doc.createTextNode(str(taxtype))
        cbcTaxTypeCode.appendChild(text)

        cacTaxScheme.appendChild(_cbcID)
        cacTaxScheme.appendChild(cbcName)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cbcPercent)
        cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
        cacTaxCategory.appendChild(cacTaxScheme)

        cacTaxSubtotal.appendChild(cbcTaxableAmount)
        cacTaxSubtotal.appendChild(_cbcTaxAmount)
        cacTaxSubtotal.appendChild(cacTaxCategory)

        cacTaxTotal.appendChild(cbcTaxAmount)
        cacTaxTotal.appendChild(cacTaxSubtotal)

        cacInvoiceLine.appendChild(cbcID)
        cacInvoiceLine.appendChild(cbcInvoicedQuantity)
        cacInvoiceLine.appendChild(cbcLineExtensionAmount)
        cacInvoiceLine.appendChild(cacPricingReference)
        cacInvoiceLine.appendChild(cacTaxTotal)
        cacInvoiceLine.appendChild(cacItem)
        cacInvoiceLine.appendChild(cacPrice)

        return cacInvoiceLine

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    def InvoiceRoot(
        self,
        rootXML,
        versionid,
        customizationid,
        id,
        issuedate,
        issuetime,
        operacion,
        invoicetypecode,
        documentcurrencycode,
    ):
        r = rootXML

        r.appendChild(self.UBLVersion(versionid))
        r.appendChild(self.CustomizationID(customizationid))

        r.appendChild(self.ID(id))
        r.appendChild(self.issueDate(issuedate))

        if issuetime:
            r.appendChild(self.issueTime(issuetime))

        r.appendChild(self.invoiceTypeCode(invoicetypecode, operacion))
        r.appendChild(self.documentCurrencyCode(documentcurrencycode))

        return r

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    ########################################################################################################################################################
    ########################################################################################################################################################
    ########################################################################################################################################################
    ########################################################################################################################################################
    ########################################################################################################################################################
    # def InvoiceRoot(self, rootXML, versionid, customizationid, id, issuedate, issuetime, invoicetypecode, documentcurrencycode, paymentduedate):
    #     r = rootXML
    #     #r.appendChild(self.firma())
    #     r.appendChild(self.UBLVersion(versionid))
    #     r.appendChild(self.CustomizationID(customizationid))
    #     # r.appendChild(self.OperacionID('02'))
    #     r.appendChild(self.ID(id))
    #     r.appendChild(self.issueDate(issuedate))
    #     if issuetime:
    #         r.appendChild(self.issueTime(issuetime))
    #     r.appendChild(self.invoiceTypeCode(invoicetypecode))
    #     r.appendChild(self.documentCurrencyCode(documentcurrencycode))
    #     # if paymentduedate:
    #     #    r.appendChild(self.PaymentDueDate(str(paymentduedate)))
    #     return r

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
    pago:Codigo de otros conceptos tributarios (Catalogo 14)
        codigo  Descripcion
        1001	Total valor de venta - operaciones gravadas
        1002	Total valor de venta - operaciones inafectas
        1003	Total valor de venta - operaciones exoneradas
        1004	Total valor de venta - operaciones gratuitas
        1005	Sub total de venta
        2001	Percepciones
        2002	Retenciones
        2003	Detracciones
        2004	Bonificaciones
        2005	Total descuentos
        3001	FISE (Ley 29852) Fondo Inclusion Social Energetico
    Parametros:
        arr_tipo_monetario:Arreglo de objetos de pago [{id:1001,monto:10.00}]
        arr_tipo_monetario:Arreglo de objetos de pago [{id:1001,value:10.00}]
    """
    # def ExtensionContent(self,arr_tipo_monetario,arr_otros):
    #     extUBLExtension = self.doc.createElement('ext:UBLExtension')

    #     extExtensionContent = self.doc.createElement('ext:ExtensionContent')
    #     extUBLExtension.appendChild(extExtensionContent)

    #     #Informacion adicional de tipo monetario
    #     sacAdditionalInformation = self.doc.createElement('sac:AdditionalInformation')
    #     extExtensionContent.appendChild(sacAdditionalInformation)

    #     for monetario in arr_tipo_monetario:
    #         id = monetario["id"]
    #         monto= monetario["monto"]
    #         sacAdditionalMonetaryTotal = self.doc.createElement('sac:AdditionalMonetaryTotal')

    #         #Codigo del Concepto Adicional
    #         cbcID = self.doc.createElement('cbc:ID')
    #         text = self.doc.createTextNode(id)
    #         cbcID.appendChild(text)
    #         sacAdditionalMonetaryTotal.appendChild(cbcID)

    #         #Monto a Pagar
    #         cbcPayableAmount = self.doc.createElement('cbc:PayableAmount')
    #         cbcPayableAmount.setAttribute('currencyID', 'PEN')
    #         text = self.doc.createTextNode(monto)
    #         cbcPayableAmount.appendChild(text)
    #         sacAdditionalMonetaryTotal.appendChild(cbcPayableAmount)

    #         sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal)

    #     for otro in arr_otros:
    #         # Informacion adicional de cualquier tipo
    #         sacAdditionalProperty = self.doc.createElement('sac:AdditionalProperty')

    #         #Codigo del concepto adicional
    #         cbcID = self.doc.createElement('cbc:ID')
    #         text = self.doc.createTextNode(otro["id"])
    #         cbcID.appendChild(text)
    #         sacAdditionalProperty.appendChild(cbcID)

    #         #Valor del Concepto
    #         cbcValue = self.doc.createElement('cbc:Value')
    #         text = self.doc.createTextNode(otro["value"])
    #         cbcValue.appendChild(text)
    #         sacAdditionalProperty.appendChild(cbcValue)

    #         sacAdditionalInformation.appendChild(sacAdditionalProperty)

    #     #extUBLExtensions.appendChild(firma())
    #     return extUBLExtension

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
        cac:item                                1
            cbc:Description                     0..n    Descripcion detallada del bien vendido o cedido en uso,
                                                        descripcion o tipo de servicio prestado por item
            cac:sellersItemIdentificaction      0..1    Identificador de elementos de item
            cbc:ID                              0..1    codigo del producto
    """
    # def cacItem(self,productID,Description):
    #     # Producto
    #     cacItem = self.doc.createElement('cac:Item')

    #     # Descripcion del Producto
    #     cbcDescription = self.doc.createElement('cbc:Description')
    #     text = self.doc.createTextNode(Description)
    #     cbcDescription.appendChild(text)
    #     cacItem.appendChild(cbcDescription)

    #     # Codigo de Producto
    #     cacSellersItemIdentification = self.doc.createElement('cac:SellersItemIdentification')
    #     cacItem.appendChild(cacSellersItemIdentification)
    #     cbcID = self.doc.createElement('cbc:ID')
    #     text = self.doc.createTextNode(productID)
    #     cbcID.appendChild(text)
    #     cacSellersItemIdentification.appendChild(cbcID)

    #     return cacItem
    """
        cac:price                   0..1
            cbc:priceAmount         1       Valores de venta unitarios por item(VU)
                                            no incluye impuestos
    """
    # def cacPrice(self,priceAmount, currencyID):
    #     # Precio del Producto
    #     cacPrice = self.doc.createElement('cac:Price')
    #     cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
    #     # cbcPriceAmount.setAttribute('currencyID', 'PEN')
    #     cbcPriceAmount.setAttribute('currencyID', currencyID)
    #     text = self.doc.createTextNode(priceAmount)
    #     cbcPriceAmount.appendChild(text)
    #     cacPrice.appendChild(cbcPriceAmount)

    #     return cacPrice

    """
        cac:PricingReference                    Valores Unitarios               0..1
            cac:AlternativeConditionPrice                                       0..n
                cbc:PriceAmount/@currencyID     Monto del valor Unitario       0..1
                cbc:PriceTypeCode               Codigo del valor unitario       0..1
    """
    # def cacPricingReference(self,precio_unitario,currencyID,no_onerosa,valor_unitario):
    #     # Valor referencial unitario por item en operaciones no onerosas y codigo
    #     cacPricingReference = self.doc.createElement('cac:PricingReference')

    #     cacAlternativeConditionPrice = self.doc.createElement('cac:AlternativeConditionPrice')
    #     # Monto de precio de venta
    #     cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
    #     cbcPriceAmount.setAttribute('currencyID', currencyID)
    #     text = self.doc.createTextNode(str(precio_unitario))
    #     cbcPriceAmount.appendChild(text)
    #     cacAlternativeConditionPrice.appendChild(cbcPriceAmount)

    #     # Codigo de Tipo de Precio de Venta (Catalogo 16)
    #     cbcPriceTypeCode = self.doc.createElement('cbc:PriceTypeCode')
    #     text = self.doc.createTextNode("01")
    #     cbcPriceTypeCode.appendChild(text)
    #     cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)
    #     cacPricingReference.appendChild(cacAlternativeConditionPrice)

    #     if no_onerosa:
    #         cacAlternativeConditionPrice02 = self.doc.createElement('cac:AlternativeConditionPrice')
    #         # Monto de precio de venta
    #         cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
    #         cbcPriceAmount.setAttribute('currencyID', currencyID)
    #         text = self.doc.createTextNode(str(valor_unitario))
    #         cbcPriceAmount.appendChild(text)
    #         cacAlternativeConditionPrice02.appendChild(cbcPriceAmount)

    #         # Codigo de Tipo de Precio de Venta (Catalogo 16)
    #         cbcPriceTypeCode = self.doc.createElement('cbc:PriceTypeCode')
    #         text = self.doc.createTextNode("02")
    #         cbcPriceTypeCode.appendChild(text)
    #         cacAlternativeConditionPrice02.appendChild(cbcPriceTypeCode)

    #         cacPricingReference.appendChild(cacAlternativeConditionPrice02)

    #     return cacPricingReference

    """
        cac:InvoiceLine                         1..n    Items de Factura
            cbc:ID                              1       Numero de orden de Item
            cbc:InvoiceQuantity/@unitCode       0..1    Unidad de medida por item(UN/ECE rec20)
            cbc:InvoiceQuantity                 0..1    Cantidad de unidades por item
            cbc:LineExtensionAmount/@currencyID 1       Moneda e importe moentario que es el total de la linea de detalle
                                                        incluyendo variaciones de precio (subvenciones, cargoso o descuentos)
                                                        pero sin impuestos
    """
    # def cacInvoiceLine(self,ID,unitCode,quantity,currencyID,amount):

    #     cacInvoiceLine = self.doc.createElement('cac:InvoiceLine')

    #     # Identificador de Item
    #     cbcID = self.doc.createElement('cbc:ID')
    #     text = self.doc.createTextNode(ID)
    #     cbcID.appendChild(text)
    #     cacInvoiceLine.appendChild(cbcID)

    #     # Cantidad del Producto
    #     cbcInvoiceQuantity = self.doc.createElement('cbc:InvoicedQuantity')

    #     # Codigo de Unidad (Anexo 3)
    #     cbcInvoiceQuantity.setAttribute('unitCode', unitCode)
    #     text = self.doc.createTextNode(quantity)
    #     cbcInvoiceQuantity.appendChild(text)
    #     cacInvoiceLine.appendChild(cbcInvoiceQuantity)

    #     # Valor de Venta por Item = valor Unitario*cantidad(Sin impuestos)
    #     cbcLineExtensionAmount = self.doc.createElement('cbc:LineExtensionAmount')
    #     cbcLineExtensionAmount.setAttribute('currencyID', currencyID)
    #     text = self.doc.createTextNode(amount)
    #     cbcLineExtensionAmount.appendChild(text)
    #     cacInvoiceLine.appendChild(cbcLineExtensionAmount)

    #     return cacInvoiceLine

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

    # def cacTaxTotal(self,tax):
    #     currencyID=tax["currencyID"]
    #     TaxAmount=tax["TaxAmount"]
    #     TaxExemptionReasonCode=tax["TaxExemptionReasonCode"]
    #     TierRange=tax["TierRange"]
    #     tributo_codigo=tax["tributo_codigo"]
    #     tributo_nombre=tax["tributo_nombre"]
    #     tributo_tipo_codigo=tax["tributo_tipo_codigo"]

    #     # Importe total de un tributo para este item
    #     cacTaxTotal = self.doc.createElement('cac:TaxTotal')

    #     # Monto de IGV de la linea
    #     cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
    #     cbcTaxAmount.setAttribute('currencyID', currencyID)
    #     text = self.doc.createTextNode(TaxAmount)
    #     cbcTaxAmount.appendChild(text)
    #     cacTaxTotal.appendChild(cbcTaxAmount)

    #     cacTaxSubtotal = self.doc.createElement('cac:TaxSubtotal')

    #     # Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
    #     cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
    #     cbcTaxAmount.setAttribute('currencyID', currencyID)
    #     text = self.doc.createTextNode(TaxAmount)
    #     cbcTaxAmount.appendChild(text)
    #     cacTaxSubtotal.appendChild(cbcTaxAmount)

    #     cacTaxCategory = self.doc.createElement('cac:TaxCategory')

    #     if tributo_codigo=="1000":
    #         # Afectacion del IGV  (Catalogo No. 07)
    #         cbcTaxExemptionReasonCode = self.doc.createElement('cbc:TaxExemptionReasonCode')
    #         text = self.doc.createTextNode(TaxExemptionReasonCode)
    #         cbcTaxExemptionReasonCode.appendChild(text)
    #         cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
    #     if tributo_codigo=="2000":
    #         #Sistema de ISC (Catalogo No 08)
    #         cbcTierRange=self.doc.createElement("cbc:TierRange")
    #         text=self.doc.createTextNode(TierRange)
    #         cbcTierRange.appendChild(text)
    #         cacTaxCategory.appendChild(cbcTierRange)

    #     # Tipo de Tributo (Catalogo No. 05)
    #     """
    #         codigo  Descripcion                              Nombre del Tipo de Codigo
    #         1000 	IGV    IMPUESTO GENERAL A LAS VENTAS     VAT
    #         2000 	ISC    IMPUESTO SELECTIVO AL CONSUMO     EXC
    #         9999 	OTROS CONCEPTOS DE PAGO				     OTH
    #     """
    #     cacTaxScheme = self.doc.createElement('cac:TaxScheme')

    #     # Tipo de Tributo:Codigo
    #     cbcID = self.doc.createElement('cbc:ID')
    #     text = self.doc.createTextNode(tributo_codigo)
    #     cbcID.appendChild(text)
    #     cacTaxScheme.appendChild(cbcID)

    #     # Tipo de Tributo: Nombre
    #     cbcName = self.doc.createElement('cbc:Name')
    #     text = self.doc.createTextNode(tributo_nombre)
    #     cbcName.appendChild(text)

    #     cacTaxScheme.appendChild(cbcName)

    #     # Tipo de Tributo: Tipo de Codigo
    #     cbcTaxTypeCode = self.doc.createElement('cbc:TaxTypeCode')
    #     text = self.doc.createTextNode(tributo_tipo_codigo)
    #     cbcTaxTypeCode.appendChild(text)
    #     cacTaxScheme.appendChild(cbcTaxTypeCode)

    #     cacTaxCategory.appendChild(cacTaxScheme)
    #     cacTaxSubtotal.appendChild(cacTaxCategory)
    #     cacTaxTotal.appendChild(cacTaxSubtotal)

    #     return cacTaxTotal

    # def AllowanceCharge(self,discount,currencyID):
    #     cacAllowanceCharge=self.doc.createElement("cac:AllowanceCharge")

    #     cbcChargeIndicator=self.doc.createElement("cbc:ChargeIndicator")
    #     text=self.doc.createTextNode("false")
    #     cbcChargeIndicator.appendChild(text)

    #     # cbcAllowanceChargeReasonCode=self.doc.createElement("cbc:AllowanceChargeReasonCode")
    #     # text=self.doc.createTextNode("00")
    #     # cbcAllowanceChargeReasonCode.appendChild(text)

    #     cbcAmount=self.doc.createElement("cbc:Amount")
    #     cbcAmount.setAttribute("currencyID",currencyID)
    #     text=self.doc.createTextNode(str(discount))
    #     cbcAmount.appendChild(text)

    #     cacAllowanceCharge.appendChild(cbcChargeIndicator)
    #     cacAllowanceCharge.appendChild(cbcAmount)

    #     return cacAllowanceCharge
    # def AllowanceCharge(self,discount,currencyID):
    #     cacAllowanceCharge=self.doc.createElement("cac:AllowanceCharge")
    #     cbcChargeIndicator=self.doc.createElement("cbc:ChargeIndicator")
    #     text=self.doc.createTextNode("false")
    #     cbcChargeIndicator.appendChild(text)
    #     cbcAmount=self.doc.createElement("cbc:Amount")
    #     cbcAmount.setAttribute("currencyID",currencyID)
    #     text=self.doc.createTextNode(str(discount))
    #     cbcAmount.appendChild(text)

    #     cacAllowanceCharge.appendChild(cbcChargeIndicator)
    #     cacAllowanceCharge.appendChild(cbcAmount)

    #     return cacAllowanceCharge

    # def InvoiceLine(self, ID, unitCode, quantity, currencyID, amount, precio_unitario, no_onerosa, valor_unitario):
    #     cacIL=self.cacInvoiceLine(ID,unitCode,quantity,currencyID,amount)
    #     cacIL.appendChild(self.cacPricingReference(precio_unitario, currencyID, no_onerosa,valor_unitario))
    #     return cacIL

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    # def IncotermsTotal(self,MontoTotal,currency_id):
    #     LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")
    #     ChargeTotalAmount = self.doc.createElement("cbc:ChargeTotalAmount")
    #     ChargeTotalAmount.setAttribute("currencyID", currency_id)
    #     text = self.doc.createTextNode(str(MontoTotal))
    #     ChargeTotalAmount.appendChild(text)
    #     LegalMonetaryTotal.appendChild(ChargeTotalAmount)
    #     return LegalMonetaryTotal

    # def LegalMonetaryTotal(self,MontoTotal,currency_id, monto_incoterms):
    #     LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")

    #     if monto_incoterms != '0.0':
    #         ChargeTotalAmount = self.doc.createElement("cbc:ChargeTotalAmount")
    #         ChargeTotalAmount.setAttribute("currencyID", currency_id)
    #         text_i = self.doc.createTextNode(monto_incoterms)
    #         ChargeTotalAmount.appendChild(text_i)
    #         LegalMonetaryTotal.appendChild(ChargeTotalAmount)

    #     PayableAmount = self.doc.createElement("cbc:PayableAmount")
    #     PayableAmount.setAttribute("currencyID", currency_id)
    #     text = self.doc.createTextNode(str(MontoTotal))
    #     PayableAmount.appendChild(text)
    #     LegalMonetaryTotal.appendChild(PayableAmount)

    #     return LegalMonetaryTotal

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    #     def AdditionalMonetaryTotal(self,currencyID,gravado,exonerado,inafecto,gratuito,total_descuento, incoterm, operacion):
    #         extUBLExtensions = self.doc.createElement("ext:UBLExtensions")
    #         extUBLExtension = self.doc.createElement("ext:UBLExtension")
    #         extExtensionContent = self.doc.createElement("ext:ExtensionContent")
    #         sacAdditionalInformation = self.doc.createElement("sac:AdditionalInformation")

    # ## ACTIVAR PARA EXPORTACION
    #         # idop = '02'
    #         idop = ''

    #         if incoterm.id != False:
    #             idop = '02'

    #         if idop is not '02':
    #             #OPERACIONES GRAVADAS
    #             sacAdditionalMonetaryTotal_gravado = self.doc.createElement("sac:AdditionalMonetaryTotal")

    #             cbcID=self.doc.createElement("cbc:ID")
    #             text=self.doc.createTextNode("1001")
    #             cbcID.appendChild(text)

    #             cbcPayableAmount=self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID",currencyID)
    #             text=self.doc.createTextNode(str(gravado))
    #             cbcPayableAmount.appendChild(text)

    #             sacAdditionalMonetaryTotal_gravado.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_gravado.appendChild(cbcPayableAmount)

    #             #OPERACIONES EXONERADAS
    #             sacAdditionalMonetaryTotal_exonerado = self.doc.createElement("sac:AdditionalMonetaryTotal")
    #             cbcID = self.doc.createElement("cbc:ID")
    #             text = self.doc.createTextNode("1003")
    #             cbcID.appendChild(text)

    #             cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID", currencyID)
    #             text = self.doc.createTextNode(str(exonerado))
    #             cbcPayableAmount.appendChild(text)

    #             sacAdditionalMonetaryTotal_exonerado.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_exonerado.appendChild(cbcPayableAmount)

    #             #OPERACIONES INAFECTAS
    #             sacAdditionalMonetaryTotal_inafecto = self.doc.createElement("sac:AdditionalMonetaryTotal")
    #             cbcID = self.doc.createElement("cbc:ID")
    #             text = self.doc.createTextNode("1002")
    #             cbcID.appendChild(text)

    #             cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID", currencyID)
    #             text = self.doc.createTextNode(str(inafecto))
    #             cbcPayableAmount.appendChild(text)

    #             sacAdditionalMonetaryTotal_inafecto.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_inafecto.appendChild(cbcPayableAmount)

    #             #OPERACIONES GRATUITAS
    #             sacAdditionalMonetaryTotal_gratuito = self.doc.createElement("sac:AdditionalMonetaryTotal")
    #             cbcID = self.doc.createElement("cbc:ID")
    #             text = self.doc.createTextNode("1004")
    #             cbcID.appendChild(text)

    #             cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID", currencyID)
    #             text = self.doc.createTextNode(str(gratuito))
    #             cbcPayableAmount.appendChild(text)

    #             sacAdditionalMonetaryTotal_gratuito.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_gratuito.appendChild(cbcPayableAmount)

    #             # DESCUENTOS
    #             sacAdditionalMonetaryTotal_descuento = self.doc.createElement("sac:AdditionalMonetaryTotal")
    #             cbcID = self.doc.createElement("cbc:ID")
    #             text = self.doc.createTextNode("2005")
    #             cbcID.appendChild(text)
    #             cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID", currencyID)
    #             text = self.doc.createTextNode(str(total_descuento))
    #             cbcPayableAmount.appendChild(text)
    #             sacAdditionalMonetaryTotal_descuento.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_descuento.appendChild(cbcPayableAmount)

    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_gravado)
    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_exonerado)
    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_inafecto)
    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_gratuito)
    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_descuento)

    #             if operacion == '04':
    #                 sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')

    #                 cbcID = self.doc.createElement('cbc:ID')
    #                 text = self.doc.createTextNode(operacion)
    #                 cbcID.appendChild(text)

    #                 sacSUNATTransaction.appendChild(cbcID)
    #                 sacAdditionalInformation.appendChild(sacSUNATTransaction)
    #         # sac:AdditionalProperty 1002 TRANSFERENCIA GRATUITA DE UN BIOEN O SERVICIO PRESTADO GRATUITAMENTE
    #         # OBLIGATORIO:
    #         """
    #             Aplicable solo en el caso que todas las operaciones (lineas o items) comprendidas en
    #             la factura electrOnica sean gratuitas.
    #             En el elemento cbc:ID se debe consignar el cOdigo 1002 (segun Catalogo No. 15).
    #         """
    #         if gratuito>0 and gravado==0 and exonerado==0 and inafecto==0  and total_descuento==0 :
    #             sacAdditionalProperty=self.doc.createElement("sac:AdditionalProperty")
    #             cbcID=self.doc.createElement("cbc:ID")
    #             text=self.doc.createTextNode("1002")
    #             cbcID.appendChild(text)
    #             cbcValue=self.doc.createElement("cbc:Value")
    #             #text=self.doc.createTextNode("TRANSFERENCIA GRATUITA DE UN BIEN Y/O SERVICIO PRESTADO GRATUITAMENTE")
    #             text=self.doc.createTextNode("TRANSFERENCIA GRATUITA")
    #             cbcValue.appendChild(text)
    #             sacAdditionalProperty.appendChild(cbcID)
    #             sacAdditionalProperty.appendChild(cbcValue)
    #             sacAdditionalInformation.appendChild(sacAdditionalProperty)

    #         # TIPO DE OPERACION
    #         if idop == '02':
    #             # OPERACIONES INAFECTAS
    #             sacAdditionalMonetaryTotal_inafecto = self.doc.createElement("sac:AdditionalMonetaryTotal")
    #             cbcID = self.doc.createElement("cbc:ID")
    #             text = self.doc.createTextNode("1002")
    #             cbcID.appendChild(text)

    #             cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
    #             cbcPayableAmount.setAttribute("currencyID", currencyID)
    #             # cambiar variable
    #             text = self.doc.createTextNode(str(exonerado))
    #             cbcPayableAmount.appendChild(text)

    #             sacAdditionalMonetaryTotal_inafecto.appendChild(cbcID)
    #             sacAdditionalMonetaryTotal_inafecto.appendChild(cbcPayableAmount)
    #             sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_inafecto)

    #             # OPERACION
    #             sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')

    #             cbcID = self.doc.createElement('cbc:ID')
    #             text = self.doc.createTextNode(idop)
    #             cbcID.appendChild(text)

    #             sacSUNATTransaction.appendChild(cbcID)
    #             sacAdditionalInformation.appendChild(sacSUNATTransaction)

    #         extExtensionContent.appendChild(sacAdditionalInformation)
    #         extUBLExtension.appendChild(extExtensionContent)

    #         extUBLExtensions.appendChild(extUBLExtension)

    #         return extUBLExtensions

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    # def TaxTotal(self,currencyID,TaxAmount,tributo_id,tributo_nombre,tributo_codigo):
    #     cacTaxTotal=self.doc.createElement("cac:TaxTotal")

    #     cbcTaxAmount=self.doc.createElement("cbc:TaxAmount")
    #     cbcTaxAmount.setAttribute("currencyID",currencyID)
    #     text=self.doc.createTextNode(str(TaxAmount))
    #     cbcTaxAmount.appendChild(text)
    #     cacTaxTotal.appendChild(cbcTaxAmount)

    #     cacTaxSubtotal=self.doc.createElement("cac:TaxSubtotal")

    #     cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
    #     cbcTaxAmount.setAttribute("currencyID", currencyID)
    #     text = self.doc.createTextNode(str(TaxAmount))
    #     cbcTaxAmount.appendChild(text)
    #     cacTaxSubtotal.appendChild(cbcTaxAmount)

    #     cacTaxCategory=self.doc.createElement("cac:TaxCategory")
    #     cacTaxScheme=self.doc.createElement("cac:TaxScheme")
    #     cbcID=self.doc.createElement("cbc:ID")
    #     text=self.doc.createTextNode(str(tributo_id))
    #     cbcID.appendChild(text)

    #     cbcName=self.doc.createElement("cbc:Name")
    #     text = self.doc.createTextNode(str(tributo_nombre))
    #     cbcName.appendChild(text)

    #     cbcTaxTypeCode = self.doc.createElement("cbc:TaxTypeCode")
    #     text = self.doc.createTextNode(str(tributo_codigo))
    #     cbcTaxTypeCode.appendChild(text)

    #     cacTaxScheme.appendChild(cbcID)
    #     cacTaxScheme.appendChild(cbcName)
    #     cacTaxScheme.appendChild(cbcTaxTypeCode)

    #     cacTaxCategory.appendChild(cacTaxScheme)

    #     cacTaxSubtotal.appendChild(cacTaxCategory)
    #     cacTaxTotal.appendChild(cacTaxSubtotal)

    #     return cacTaxTotal

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    def sendBill(self, username, password, namefile, contentfile):
        Envelope = self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute(
            "xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/"
        )
        Envelope.setAttribute("xmlns:ser", "http://service.sunat.gob.pe")
        Envelope.setAttribute(
            "xmlns:wsse",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
        )

        Header = self.doc.createElement("soapenv:Header")
        Security = self.doc.createElement("wsse:Security")
        UsernameToken = self.doc.createElement("wsse:UsernameToken")
        Username = self.doc.createElement("wsse:Username")
        text = self.doc.createTextNode(username)
        Username.appendChild(text)
        Password = self.doc.createElement("wsse:Password")
        text = self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body = self.doc.createElement("soapenv:Body")
        sendBill = self.doc.createElement("ser:sendBill")
        fileName = self.doc.createElement("fileName")
        text = self.doc.createTextNode(namefile)
        fileName.appendChild(text)
        contentFile = self.doc.createElement("contentFile")
        text = self.doc.createTextNode(contentfile)
        contentFile.appendChild(text)
        sendBill.appendChild(fileName)
        sendBill.appendChild(contentFile)
        Body.appendChild(sendBill)
        Envelope.appendChild(Body)

        return Envelope

    def getStatus(self, username, password, ruc, tipo, numero):
        Envelope = self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute(
            "xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/"
        )
        Envelope.setAttribute("xmlns:ser", "http://service.sunat.gob.pe")
        Envelope.setAttribute(
            "xmlns:wsse",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
        )

        Header = self.doc.createElement("soapenv:Header")
        Security = self.doc.createElement("wsse:Security")
        UsernameToken = self.doc.createElement("wsse:UsernameToken")
        Username = self.doc.createElement("wsse:Username")
        text = self.doc.createTextNode(ruc + username)
        Username.appendChild(text)
        Password = self.doc.createElement("wsse:Password")
        text = self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body = self.doc.createElement("soapenv:Body")
        getStatus = self.doc.createElement("ser:getStatus")
        nruc = self.doc.createElement("rucComprobante")
        text = self.doc.createTextNode(ruc)
        nruc.appendChild(text)
        ntipo = self.doc.createElement("tipoComprobante")
        text = self.doc.createTextNode(tipo)
        ntipo.appendChild(text)
        serie = self.doc.createElement("serieComprobante")
        text = self.doc.createTextNode(numero[:-9])
        serie.appendChild(text)
        num = self.doc.createElement("numeroComprobante")
        v = numero[6:]
        text = self.doc.createTextNode(str(int(v)))
        num.appendChild(text)
        getStatus.appendChild(nruc)
        getStatus.appendChild(ntipo)
        getStatus.appendChild(serie)
        getStatus.appendChild(num)
        Body.appendChild(getStatus)
        Envelope.appendChild(Body)

        return Envelope

    #########################################################################
    #########################################################################
    ## /Invoice/cac:PrepaidPayment/cbc:ID (Identificador del pago)
    ## /Invoice/cac:PrepaidPayment/cbc:ID@schemeName (Anticipo)
    ## /Invoice/cac:PrepaidPayment/cbc:PaidAmount (Monto anticipado)
    ## /Invoice/cac:PrepaidPayment/cbc:PaidAmount@currencyID
    ## /Invoice/cac:AdditionalDocumentReference/cbc:DocumentStatusCode (Identificador del pago)
    ## /Invoice/cac:AdditionalDocumentReference/cbc:DocumentStatusCode@listName (Anticipo)
    ## /Invoice/cac:AdditionalDocumentReference/cbc:ID (Serie y Numero de comprobante que se realizo el anticipo)
    ## /Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode (Tipo de comprobante que se realizo el anticipo)
    ## /Invoice/cac:AdditionalDocumentReference/cbc:DocumentTypeCode@listName (Documento Relacionado)
    ## /Invoice/cac:AdditionalDocumentReference/cac:IssuerParty/cac:PartyIdentification/cbc:ID (Numero de documento del emisor del anticipo)
    ## /Invoice/cac:AdditionalDocumentReference/cac:IssuerParty/cac:PartyIdentification/cbc:ID@schemeID (Tipo de documento del emisor del anticipo)(6)
    ## /Invoice/cac:LegalMonetaryTotal/cbc:PrepaidAmount (Total de anticipos)
    ## /Invoice/cac:LegalMonetaryTotal/cbc:PrepaidAmount@currencyID
    #########################################################################
    #########################################################################
