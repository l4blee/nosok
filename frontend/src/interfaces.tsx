type VarsBlock = {cpu_used: number, memory_used: number}
type VarsPayload = {status: string, servers: number, vars: VarsBlock}

type RuntimeData = {status: string, servers: number, vars: VarsBlock[]}
type RuntimeStatsStorage = {log: string, overview: RuntimeData}

type PollingPayload = {changed: string, content: string | VarsPayload}
type APIPayload = {message: string, content: string | VarsPayload}

export type {VarsBlock, RuntimeData, RuntimeStatsStorage, PollingPayload, APIPayload, VarsPayload}