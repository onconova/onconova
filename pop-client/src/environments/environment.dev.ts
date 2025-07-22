import { dynamicEnv} from './dynamic-env';

export const environment: any = {
    production: false,
    organizationName: dynamicEnv.organizationName
};
  