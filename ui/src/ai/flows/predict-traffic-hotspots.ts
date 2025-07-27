'use server';
/**
 * @fileOverview Traffic hotspot prediction flow.
 *
 * - predictTrafficHotspots - A function that predicts traffic hotspots based on real-time and historical data.
 * - PredictTrafficHotspotsInput - The input type for the predictTrafficHotspots function.
 * - PredictTrafficHotspotsOutput - The return type for the predictTrafficHotspots function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const PredictTrafficHotspotsInputSchema = z.object({
  currentVehicleRoutes: z.string().describe('JSON array of current vehicle routes with vehicle ID and route waypoints.'),
  historicalTrafficData: z.string().describe('JSON array of historical traffic data with timestamps and traffic density.'),
});
export type PredictTrafficHotspotsInput = z.infer<typeof PredictTrafficHotspotsInputSchema>;

const PredictTrafficHotspotsOutputSchema = z.object({
  predictedHotspots: z.string().describe('JSON array of predicted traffic hotspots with location, severity, and predicted time.'),
  suggestedReroutes: z.string().describe('JSON array of suggested reroutes for vehicles to avoid hotspots, with vehicle ID and new route waypoints.'),
});
export type PredictTrafficHotspotsOutput = z.infer<typeof PredictTrafficHotspotsOutputSchema>;

export async function predictTrafficHotspots(input: PredictTrafficHotspotsInput): Promise<PredictTrafficHotspotsOutput> {
  return predictTrafficHotspotsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'predictTrafficHotspotsPrompt',
  input: {schema: PredictTrafficHotspotsInputSchema},
  output: {schema: PredictTrafficHotspotsOutputSchema},
  prompt: `You are an AI-powered traffic prediction system designed to identify and mitigate traffic congestion in urban environments.

  Analyze the provided real-time vehicle routes and historical traffic data to predict potential traffic hotspots and suggest reroutes to minimize congestion.

  Current Vehicle Routes:
  {{currentVehicleRoutes}}

  Historical Traffic Data:
  {{historicalTrafficData}}

  Based on this information, predict future traffic hotspots, including their location, severity, and predicted time of occurrence. Also, provide optimized reroutes for specific vehicles to avoid these hotspots.
  Return the hotspots and reroutes as JSON arrays.

  Ensure that the data is valid JSON and that the reroutes correspond to vehicles listed in the input.
  `,
});

const predictTrafficHotspotsFlow = ai.defineFlow(
  {
    name: 'predictTrafficHotspotsFlow',
    inputSchema: PredictTrafficHotspotsInputSchema,
    outputSchema: PredictTrafficHotspotsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
