import { dynamicEnv} from './dynamic-env';

export const environment: any = {
    production: false,
    apiServerBasePath: `https://${dynamicEnv.apiServerHost}:${dynamicEnv.apiServerPort}` || '${window.location.protocol}//${window.location.host}',
    organizationName: dynamicEnv.organizationName
};
  