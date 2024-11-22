export * from './auth.service';
import { AuthService } from './auth.service';
export * from './auth.serviceInterface';
export * from './cancer-patients.service';
import { CancerPatientsService } from './cancer-patients.service';
export * from './cancer-patients.serviceInterface';
export const APIS = [AuthService, CancerPatientsService];
