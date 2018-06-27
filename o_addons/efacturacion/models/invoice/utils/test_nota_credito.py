import NotaCredito

notaCredito = NotaCredito.NotaCredito()

nota_credito = notaCredito.NotaCreditoRoot("2.1", "2.0", "FC01-211", "2018-01-23", "20:25:52", "PEN", "050100201170625")
discrepancy_response = notaCredito.DiscrepancyResponse("FC01-4355", "07", "Unidades defectuosas")
billing_reference = notaCredito.BillingReference("FC01-4355", "01")
signature = notaCredito.Signature("IDSignSt", "20100454523", "SOPORTE TECNOLOGICOS EIRL", "#SignatureSP")
supplier_party = notaCredito.AccountingSupplierParty("Tu Soporte", "SOPORTE TECNOLOGICOS EIRL", "20100454523", "0001",
                                                     "-")
customer_party = notaCredito.AccountingCustomerParty("Servicabinas S.A.", "20587896411", "-")
tax_total = notaCredito.TaxTotal("1494.92", "8305.08", "1494.92", "1000", "IGV", "VAT")
legal_monetary = notaCredito.LegalMonetaryTotal("8379")
credit_note_line = notaCredito.CreditNoteLine("1", "100", "8305.08", "98.00", "1494.92", "8305.08", "1494.92", "10",
                                              "1000", "IGV", "VAT", "Grabadora LG Externo Modelo: GE20LU10", "GLG199",
                                              "45111723", "83.05")

nota_credito.appendChild(discrepancy_response)
nota_credito.appendChild(billing_reference)
nota_credito.appendChild(signature)
nota_credito.appendChild(supplier_party)
nota_credito.appendChild(customer_party)
nota_credito.appendChild(tax_total)
nota_credito.appendChild(legal_monetary)
nota_credito.appendChild(credit_note_line)

nota_credito = nota_credito.toprettyxml(indent=" ")

# print nota_credito
