'use server';

/**
 * @fileOverview A flow for generating alert messages for the admin dashboard, including recommended actions based on predictive analysis.
 *
 * - generateAlertMessage - A function that generates an alert message with recommended actions.
 * - GenerateAlertMessageInput - The input type for the generateAlertMessage function.
 * - GenerateAlertMessageOutput - The return type for the generateAlertMessage function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateAlertMessageInputSchema = z.object({
  journeyId: z.string().describe('The ID of the journey associated with the alert.'),
  alertType: z.string().describe('The type of alert (e.g., Predictive Gridlock).'),
  message: z.string().describe('A detailed message describing the alert.'),
  predictedDelayMinutes: z.number().describe('The predicted delay in minutes.'),
  affectedRouteId: z.string().describe('The ID of the affected route.'),
  currentVehicleLocation: z.string().describe('The vehicles current location as a latitudinal longitude pair'),
  recommendedAction: z.string().describe('The AI recommended action as a textual description'),
});

export type GenerateAlertMessageInput = z.infer<typeof GenerateAlertMessageInputSchema>;

const GenerateAlertMessageOutputSchema = z.object({
  alertId: z.string().describe('A unique ID for the alert.'),
  journeyId: z.string().describe('The ID of the journey associated with the alert.'),
  timestamp: z.string().describe('The timestamp when the alert was generated.'),
  alertType: z.string().describe('The type of alert (e.g., Predictive Gridlock).'),
  message: z.string().describe('A detailed message describing the alert.'),
  recommendedAction: z.string().describe('A clear, concise recommended action to address the alert.'),
  newRouteId: z.string().optional().describe('The ID of the suggested new route, if rerouting is recommended.'),
});

export type GenerateAlertMessageOutput = z.infer<typeof GenerateAlertMessageOutputSchema>;

export async function generateAlertMessage(input: GenerateAlertMessageInput): Promise<GenerateAlertMessageOutput> {
  return generateAlertMessageFlow(input);
}

const generateAlertMessagePrompt = ai.definePrompt({
  name: 'generateAlertMessagePrompt',
  input: {schema: GenerateAlertMessageInputSchema},
  output: {schema: GenerateAlertMessageOutputSchema},
  prompt: `You are an AI assistant that generates alert messages for an urban mobility management system.

  Given the following information about a potential traffic incident, generate a clear and concise alert message with a recommended action for the admin dashboard.

  Journey ID: {{{journeyId}}}
  Alert Type: {{{alertType}}}
  Message: {{{message}}}
  Predicted Delay: {{{predictedDelayMinutes}}} minutes
  Affected Route ID: {{{affectedRouteId}}}
  Vehicle Location: {{{currentVehicleLocation}}}
  AI Recommended Action: {{{recommendedAction}}}

  Generate a recommended action that is specific and actionable. If rerouting is suggested, mention that a new route ID will be provided.

  Output the alert in the following JSON format:
  {
    "alertId": "<unique_alert_id>",
    "journeyId": "{{{journeyId}}}",
    "timestamp": "<current_timestamp>",
    "alertType": "{{{alertType}}}",
    "message": "{{{message}}}",
    "recommendedAction": "<recommended_action>",
    "newRouteId": "<new_route_id>" // Only include if rerouting is suggested
  }`,
});

const generateAlertMessageFlow = ai.defineFlow(
  {
    name: 'generateAlertMessageFlow',
    inputSchema: GenerateAlertMessageInputSchema,
    outputSchema: GenerateAlertMessageOutputSchema,
  },
  async input => {
    const timestamp = new Date().toISOString();
    const alertId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

    const {output} = await generateAlertMessagePrompt({
      ...input,
      alertId: alertId,
      timestamp: timestamp,
    });

    return {
      ...output,
      alertId: alertId,
      timestamp: timestamp,
    } as GenerateAlertMessageOutput;
  }
);
