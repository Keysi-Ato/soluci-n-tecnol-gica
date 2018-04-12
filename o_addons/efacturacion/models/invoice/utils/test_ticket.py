import Boleta

boleta = Boleta.Boleta()

ticket = boleta.SummaryRoot("2.0", "1.0", "RC-20181234-008",
                            "2018-01-23", "2018-01-24", "Note 1")
signature = boleta.Signature("IdSignCA", "20100113612", "Corporation", "SignatureUri")
accounting_supplier_party = boleta.AccountingSupplierParty("201001136120", "6", "Corporation")
summary_line = boleta.SummaryLine("1", "03", "DA45", "456", "764", "117350.75",
                                  ["78223.00", "24423.00", "0.00"], "01", "true", "5.00",
                                  [{"TaxAmount": "0.00",
                                    "tributo_codigo": "2000",
                                    "tributo_nombre": "ISC",
                                    "tributo_tipo_codigo": "EXC"}, {"TaxAmount": "1010.00",
                                                                    "tributo_codigo": "1000",
                                                                    "tributo_nombre": "IGV",
                                                                    "tributo_tipo_codigo": "VAT"},
                                   {"TaxAmount": "1010.00",
                                    "tributo_codigo": "1000",
                                    "tributo_nombre": "OTROS",
                                    "tributo_tipo_codigo": "VAT"}]
                                  )

summary_line_2 = boleta.SummaryLine("2", "03", "DA45", "456", "764", "117350.75",
                                    ["78223.00", "24423.00", "15.00"], "01", "true", "5.00",
                                    [{"TaxAmount": "0.00",
                                      "tributo_codigo": "2000",
                                      "tributo_nombre": "ISC",
                                      "tributo_tipo_codigo": "EXC"}, {"TaxAmount": "1010.00",
                                                                      "tributo_codigo": "1000",
                                                                      "tributo_nombre": "IGV",
                                                                      "tributo_tipo_codigo": "VAT"},
                                     {"TaxAmount": "1010.00",
                                      "tributo_codigo": "1000",
                                      "tributo_nombre": "OTROS",
                                      "tributo_tipo_codigo": "VAT"}]
                                    )

ticket.appendChild(signature)
ticket.appendChild(accounting_supplier_party)
ticket.appendChild(summary_line)
ticket.appendChild(summary_line_2)
ticket = ticket.toprettyxml(indent=" ")

print(ticket)
