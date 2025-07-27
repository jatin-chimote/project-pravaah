import { config } from 'dotenv';
config();

import '@/ai/flows/predict-traffic-hotspots.ts';
import '@/ai/flows/generate-alert-messages.ts';
import '@/ai/flows/dynamically-reroute-vehicles.ts';
import '@/ai/flows/report-hazard-flow.ts';
