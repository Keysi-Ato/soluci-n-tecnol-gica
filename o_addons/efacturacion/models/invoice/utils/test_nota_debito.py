import NotaDebito

notaDebito = NotaDebito.NotaDebito()

nota_debito = notaDebito.NotaDebitoRoot("2.0", "1.0", "F001-0007", "2018-01-23", "PEN")
discrepancy_response = notaDebito.DiscrepancyResponse("F001-4355", "01", "Aplicacion de intereses")
billing_reference = notaDebito.BillingReference("F001-4355", "01")
signature = notaDebito.Signature("IDSignSP", "20100454523", "SOPORTE TECNOLOGICOS EIRL", "#SignatureSP")
supplier_party = notaDebito.AccountingSupplierParty("20100454523", "6", "SOPORTE TECNOLOGICOS EIRL", "0000")
customer_party = notaDebito.AccountingCustomerParty("20587896411",  "6", "Servicabinas S.A.")
tax_total = notaDebito.TaxTotal("1145.55", "1145.55", "1000", "IGV", "VAT")
legal_monetary = notaDebito.RequestedMonetaryTotal("7509.71")
credit_note_line = notaDebito.DebitNoteLine("1", "1", "6364.16", "7509.71", "01", "1145.55", "1145.55", "10", "1000", "IGV",
                                            "VAT", "Cobro de intereses por pago fuera de fecha", "45111723", "6364.16")

nota_debito.appendChild(discrepancy_response)
nota_debito.appendChild(billing_reference)
nota_debito.appendChild(signature)
nota_debito.appendChild(supplier_party)
nota_debito.appendChild(customer_party)
nota_debito.appendChild(tax_total)
nota_debito.appendChild(legal_monetary)
nota_debito.appendChild(credit_note_line)

nota_debito = nota_debito.toprettyxml(indent=" ")

print nota_debito
