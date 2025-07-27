// This file is machine-generated - edit at your own risk.

'use server';

/**
 * @fileOverview A dynamic vehicle rerouting AI agent that suggests new routes based on predicted traffic conditions.
 *
 * - dynamicallyRerouteVehicles - A function that handles the rerouting process.
 * - DynamicallyRerouteVehiclesInput - The input type for the dynamicallyRerouteVehicles function.
 * - DynamicallyRerouteVehiclesOutput - The return type for the dynamicallyRerouteVehicles function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const DynamicallyRerouteVehiclesInputSchema = z.object({
  routeId: z.string().describe('The ID of the route to be analyzed.'),
  vehicleId: z.string().describe('The ID of the vehicle currently on the route.'),
  currentTrafficData: z.string().describe('Real-time traffic data for the route.'),
  historicalTrafficPatterns: z.string().describe('Historical traffic patterns for the route.'),
});
export type DynamicallyRerouteVehiclesInput = z.infer<typeof DynamicallyRerouteVehiclesInputSchema>;

const DynamicallyRerouteVehiclesOutputSchema = z.object({
  shouldReroute: z.boolean().describe('Whether or not the vehicle should be rerouted.'),
  newRouteId: z.string().describe('The ID of the suggested new route, if rerouting is recommended.'),
  reason: z.string().describe('The reason for the rerouting recommendation.'),
});
export type DynamicallyRerouteVehiclesOutput = z.infer<typeof DynamicallyRerouteVehiclesOutputSchema>;

export async function dynamicallyRerouteVehicles(input: DynamicallyRerouteVehiclesInput): Promise<DynamicallyRerouteVehiclesOutput> {
  return dynamicallyRerouteVehiclesFlow(input);
}

const dynamicallyRerouteVehiclesPrompt = ai.definePrompt({
  name: 'dynamicallyRerouteVehiclesPrompt',
  input: {schema: DynamicallyRerouteVehiclesInputSchema},
  output: {schema: DynamicallyRerouteVehiclesOutputSchema},
  prompt: `You are an AI assistant designed to analyze traffic conditions and suggest optimal routes for vehicles.

You are provided with real-time traffic data, historical traffic patterns, the current route ID, and the vehicle ID.

Analyze the provided information and determine if the vehicle should be rerouted.

If rerouting is recommended, provide a new route ID and a clear reason for the rerouting recommendation.

If rerouting is not necessary, indicate that the vehicle should not be rerouted and provide a reason.

Real-time Traffic Data: {{{currentTrafficData}}}
Historical Traffic Patterns: {{{historicalTrafficPatterns}}}
Current Route ID: {{{routeId}}}
Vehicle ID: {{{vehicleId}}}

Based on this information, should the vehicle be rerouted? Provide your response in JSON format.
`,
});

const dynamicallyRerouteVehiclesFlow = ai.defineFlow(
  {
    name: 'dynamicallyRerouteVehiclesFlow',
    inputSchema: DynamicallyRerouteVehiclesInputSchema,
    outputSchema: DynamicallyRerouteVehiclesOutputSchema,
  },
  async input => {
    const {output} = await dynamicallyRerouteVehiclesPrompt(input);
    return output!;
  }
);
