const coreConfig = (window as any).coreConfig || {}
const pluginsConfig = (window as any).pluginsConfig || {}

export const dynamicEnv: any = {...coreConfig, ...pluginsConfig};
