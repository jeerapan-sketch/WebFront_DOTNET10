export type Chb1Scope = { tenantId: string; warehouseId: string; invoiceNo: string; revisionId: string; processingRunId: string; schemaVersion?: number }
export type Chb1Column = { key: string; label: string; format: string; width: number }
export type Chb1Values = Record<string, string | number | null>
export type Chb1Report = { scope: Chb1Scope; companyName: string; title: string; warnings: string[]; columns: Chb1Column[]; rows: Chb1Values[]; totals: Chb1Values }
