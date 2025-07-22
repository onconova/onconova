import { dynamicEnv} from './dynamic-env';

export const environment: any = {
  production: true,
  organizationName: dynamicEnv.organizationName
};
