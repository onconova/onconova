import { dynamicEnv} from './dynamic-env';

export const environment: any = {
  production: false,
  apiServerBasePath: dynamicEnv.popServerAddress ? `https://${dynamicEnv.popServerAddress}` : `${window.location.protocol}//${window.location.host}`,
  docsServerBasePath: dynamicEnv.docsServerAddress ? `https://${dynamicEnv.docsServerAddress}` : `${window.location.protocol}//${window.location.host}`,
  organizationName: dynamicEnv.organizationName
};

  