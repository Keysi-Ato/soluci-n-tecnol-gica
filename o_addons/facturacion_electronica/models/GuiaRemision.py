from xml.dom import minidom


class GuiaRemision:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement("DespatchAdvice")
        self.doc.appendChild(root)
        root.setAttribute(
            "xmlns", "urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
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
        cbcInvoiceTypeCode = self.doc.createElement("cbc:DespatchAdviceTypeCode")
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

    def cacOrderReference(self, documento, num_doc_ident, tipo_doc_ident):
        cacOrderReference = self.doc.createElement(
            "cac:OrderReference"
        )
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(documento)
        cbcID.appendChild(text)

        cbcDocumentTypeCode = self.doc.createElement("cbc:OrderTypeCode")
        text = self.doc.createTextNode("09")
        cbcDocumentTypeCode.appendChild(text)

        cacOrderReference.appendChild(cbcID)
        cacOrderReference.appendChild(cbcDocumentTypeCode)

        return cacOrderReference

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

        cacAdditionalDocumentReference.appendChild(cbcID)
        cacAdditionalDocumentReference.appendChild(cbcDocumentTypeCode)

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
        cacAccountingSupplierParty = self.doc.createElement("cac:DespatchSupplierParty")

        cbcID = self.doc.createElement("cbc:CustomerAssignedAccountID")
        cbcID.setAttribute("schemeID", tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcID.appendChild(text)
        
        cacParty = self.doc.createElement("cac:Party")
        cacPartyLegalEntity = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName")
        text = self.doc.createTextNode(nombre_comercial)
        cbcRegistrationName.appendChild(text)

        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        cacParty.appendChild(cacPartyLegalEntity)

        cacAccountingSupplierParty.appendChild(cbcID)
        cacAccountingSupplierParty.appendChild(cacParty)

        return cacAccountingSupplierParty

    def cacSellerSupplierParty(#
        self,
        num_doc_ident,
        tipo_doc_ident,
        nombre_comercial,
    ):
        cacSellerSupplierParty = self.doc.createElement("cac:SellerSupplierParty")

        cbcID = self.doc.createElement("cbc:CustomerAssignedAccountID")
        cbcID.setAttribute("schemeID", tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcID.appendChild(text)
        
        cacParty = self.doc.createElement("cac:Party")
        cacPartyLegalEntity = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName")
        text = self.doc.createTextNode(nombre_comercial)
        cbcRegistrationName.appendChild(text)

        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        cacParty.appendChild(cacPartyLegalEntity)

        cacSellerSupplierParty.appendChild(cbcID)
        cacSellerSupplierParty.appendChild(cacParty)

        return cacSellerSupplierParty


    def cacAccountingCustomerParty(
        self, num_doc_identidad, tipo_doc_identidad, nombre_cliente
    ):
        cacAccountingCustomerParty = self.doc.createElement("cac:DeliveryCustomerParty")

        cbcID = self.doc.createElement("cbc:CustomerAssignedAccountID")
        cbcID.setAttribute("schemeID", tipo_doc_identidad)
        text = self.doc.createTextNode(num_doc_identidad)
        cbcID.appendChild(text)

        cacParty = self.doc.createElement("cac:Party")
        cacPartyLegalEntity = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName")
        text = self.doc.createTextNode(nombre_cliente)
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        cacParty.appendChild(cacPartyLegalEntity)

        cacAccountingCustomerParty.appendChild(cbcID)
        cacAccountingCustomerParty.appendChild(cacParty)

        return cacAccountingCustomerParty

    def cacShipment(
        self, ruc_trans,tipo_doc_identidad_trans,razon_social,placa_vehiculo,dni_conductor,
            tipo_doc_identidad_cond,motivo_traslado,descrip_motiv_traslado,indicador_transbordo,
            peso_bruto_total,unidad_medida_peso,numero_de_bulto,modalidad_traslado,fecha_inicio_traslado,
            ubigeo_punto_partida,direccion_punto_partida,ubigeo_punto_llegada,direccion_punto_llegada,
            codigo_puerto_embarque,codigo_puerto_desembarque,codigo_contenedor,id
    ):
        cacShipment = self.doc.createElement("cac:Shipment")#transporte
        cbcId = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)#motivo de traslado
        cbcId.appendChild(text)
        cbcHandlingCode = self.doc.createElement("cbc:HandlingCode")
        text = self.doc.createTextNode(motivo_traslado)#motivo de traslado
        cbcHandlingCode.appendChild(text)
        cbcInformation = self.doc.createElement("cbc:Information")
        text = self.doc.createTextNode(descrip_motiv_traslado)#descripcion motivo
        cbcInformation.appendChild(text)
        cbcGrossWeightMeasure = self.doc.createElement("cbc:GrossWeightMeasure")
        cbcGrossWeightMeasure.setAttribute("unitCode", tipo_doc_identidad_trans)
        text = self.doc.createTextNode(peso_bruto_total)#peso bruto total 
        cbcGrossWeightMeasure.appendChild(text)
        cbcTotalTransportHandlingUnitQuantity = self.doc.createElement("cbc:TotalTransportHandlingUnitQuantity")
        text = self.doc.createTextNode(numero_de_bulto)#numero de bulto
        cbcTotalTransportHandlingUnitQuantity.appendChild(text)
        cbcSplitConsignmentIndicator = self.doc.createElement("cbc:SplitConsignmentIndicator")
        text = self.doc.createTextNode(indicador_transbordo)#indicador de transbordo
        cbcSplitConsignmentIndicator.appendChild(text)#
        cacShipmentStage = self.doc.createElement("cac:ShipmentStage")#cacShipmentStage
        cbcTransportModeCode = self.doc.createElement("cbc:TransportModeCode")
        text = self.doc.createTextNode(modalidad_traslado)#modalidad de traslado
        cbcTransportModeCode.appendChild(text)
        cacTransitPeriod = self.doc.createElement("cac:TransitPeriod")
        cbcStartDate = self.doc.createElement("cbc:StartDate")
        text = self.doc.createTextNode(fecha_inicio_traslado)# fecha inicio traslado
        cbcStartDate.appendChild(text)
        cacTransitPeriod.appendChild(cbcStartDate)
        cacCarrierParty = self.doc.createElement("cac:CarrierParty")
        cacPartyIdentification = self.doc.createElement("cac:PartyIdentification")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ruc_trans)#ruc_trans
        cbcID.appendChild(text)
        cacPartyIdentification.appendChild(cbcID)
        cacPartyName = self.doc.createElement("cac:PartyName")
        cbcName = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(razon_social)#razon_social
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)
        cacCarrierParty.appendChild(cacPartyIdentification)
        cacCarrierParty.appendChild(cacPartyName)#cac:CarrierParty
        cacTransportMeans = self.doc.createElement("cac:TransportMeans")
        cacRoadTransport = self.doc.createElement("cac:RoadTransport")
        cbcLicensePlateID = self.doc.createElement("cbc:LicensePlateID")
        text = self.doc.createTextNode(placa_vehiculo)#placa vehiculo 
        cbcLicensePlateID.appendChild(text)
        cacRoadTransport.appendChild(cbcLicensePlateID)
        cacTransportMeans.appendChild(cacRoadTransport)
        cacDriverPerson = self.doc.createElement("cac:DriverPerson")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(dni_conductor)#dni conductor
        cbcID.appendChild(text)
        cacDriverPerson.appendChild(cbcID)
        cacShipmentStage.appendChild(cbcTransportModeCode)
        cacShipmentStage.appendChild(cacTransitPeriod)
        cacShipmentStage.appendChild(cacCarrierParty)
        cacShipmentStage.appendChild(cacTransportMeans)
        cacShipmentStage.appendChild(cacDriverPerson)#cacShipmentStage
        cacDelivery = self.doc.createElement("cac:Delivery")
        cacDeliveryAddress = self.doc.createElement("cac:DeliveryAddress")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo_punto_llegada)#ubigeo punto llegada
        cbcID.appendChild(text)
        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion_punto_llegada)#direccion punto llegada
        cbcStreetName.appendChild(text)
        cacDeliveryAddress.appendChild(cbcID)
        cacDeliveryAddress.appendChild(cbcStreetName)
        cacDelivery.appendChild(cacDeliveryAddress)

        cacTransportHandlingUnit = self.doc.createElement("cac:TransportHandlingUnit")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(codigo_contenedor)#contenedor
        cbcID.appendChild(text)
        cacTransportHandlingUnit.appendChild(cbcID)

        cacOriginAddress = self.doc.createElement("cac:OriginAddress")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo_punto_partida)#ubigeo punto partida
        cbcID.appendChild(text)
        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion_punto_partida)#direccion punto partida
        cbcStreetName.appendChild(text)
        cacOriginAddress.appendChild(cbcID)
        cacOriginAddress.appendChild(cbcStreetName)
        cacFirstArrivalPortLocation = self.doc.createElement("cac:FirstArrivalPortLocation")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(codigo_puerto_embarque)
        cbcID.appendChild(text)
        cacFirstArrivalPortLocation.appendChild(cbcID)

        cacShipment.appendChild(cbcId)
        cacShipment.appendChild(cbcHandlingCode)
        if descrip_motiv_traslado != 'False' : 
            cacShipment.appendChild(cbcInformation)
        cacShipment.appendChild(cbcGrossWeightMeasure)
        cacShipment.appendChild(cbcTotalTransportHandlingUnitQuantity)
        if indicador_transbordo != 'False' :
            cacShipment.appendChild(cbcSplitConsignmentIndicator)
        cacShipment.appendChild(cacShipmentStage)
        cacShipment.appendChild(cacDelivery)
        if codigo_contenedor != 'False' : # si existe contenedor
            cacShipment.appendChild(cacTransportHandlingUnit)
        cacShipment.appendChild(cacOriginAddress)
        if codigo_puerto_embarque != 'False' : # si existe puerto embarque
            cacShipment.appendChild(cacFirstArrivalPortLocation)

        return cacShipment

    
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
    def cacDespatchLine(
        self,
        operacionTipo,
        idline,
        muestra,
        unitcode,
        quantity,
        description,
    ):
        # Definimos variables a usar en el esquema

        cacDespatchLine = self.doc.createElement("cac:DespatchLine")

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(idline))
        cbcID.appendChild(text)

        cbcInvoicedQuantity = self.doc.createElement("cbc:DeliveredQuantity")
        cbcInvoicedQuantity.setAttribute("unitCode", unitcode)
        text = self.doc.createTextNode(quantity)
        cbcInvoicedQuantity.appendChild(text)

        cacOrderLineReference = self.doc.createElement("cac:OrderLineReference")
        cbcLineID = self.doc.createElement("cbc:LineID")
        text = self.doc.createTextNode(str(idline))
        cbcLineID.appendChild(text)
        cacOrderLineReference.appendChild(cbcLineID)

        cacItem = self.doc.createElement("cac:Item")
        cbcName = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(description)
        cbcName.appendChild(text)
        cacSellersItemIdentification = self.doc.createElement("cac:SellersItemIdentification")
        cbcIDd = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(idline))
        cbcIDd.appendChild(text)
        cacSellersItemIdentification.appendChild(cbcIDd)
        cacCommodityClassification = self.doc.createElement("cac:CommodityClassification")
        cbcItemClassificationCode = self.doc.createElement("cbc:ItemClassificationCode")
        text = self.doc.createTextNode(str(idline))
        cbcItemClassificationCode.appendChild(text)
        cacCommodityClassification.appendChild(cbcItemClassificationCode)

        cacItem.appendChild(cbcName)
        cacItem.appendChild(cacSellersItemIdentification)
        cacItem.appendChild(cacCommodityClassification)

        cacDespatchLine.appendChild(cbcID)
        cacDespatchLine.appendChild(cbcInvoicedQuantity)
        cacDespatchLine.appendChild(cacOrderLineReference)
        cacDespatchLine.appendChild(cacItem)#

        return cacDespatchLine

    
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
        note,
    ):
        r = rootXML

        r.appendChild(self.UBLVersion(versionid))
        r.appendChild(self.CustomizationID(customizationid))

        r.appendChild(self.ID(id))
        r.appendChild(self.issueDate(issuedate))

        if issuetime:
            r.appendChild(self.issueTime(issuetime))

        r.appendChild(self.invoiceTypeCode(invoicetypecode, operacion))
        #r.appendChild(self.documentCurrencyCode(documentcurrencycode))
        cbcnote = self.doc.createElement("cbc:Note")
        text = self.doc.createTextNode(note)
        cbcnote.appendChild(text)
        r.appendChild(cbcnote)
        return r

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

