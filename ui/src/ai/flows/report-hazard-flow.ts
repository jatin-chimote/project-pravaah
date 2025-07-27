
'use server';

/**
 * @fileOverview A flow for drivers to report road hazards with a photo and description.
 *
 * - reportHazard - A function that handles the hazard reporting process.
 * - ReportHazardInput - The input type for the reportHazard function.
 * - ReportHazardOutput - The return type for the reportHazard function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const ReportHazardInputSchema = z.object({
  photoDataUri: z
    .string()
    .describe(
      "A photo of the hazard, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
  description: z.string().describe('A description of the hazard provided by the driver.'),
  location: z.object({
    lat: z.number(),
    lng: z.number(),
  }).describe('The geographical location where the hazard was reported.'),
});
export type ReportHazardInput = z.infer<typeof ReportHazardInputSchema>;

const ReportHazardOutputSchema = z.object({
  reportId: z.string().describe('A unique ID for the hazard report.'),
  status: z.string().describe('The status of the report (e.g., "Received", "Under Review").'),
  message: z.string().describe('A confirmation message for the driver.'),
});
export type ReportHazardOutput = z.infer<typeof ReportHazardOutputSchema>;

export async function reportHazard(input: ReportHazardInput): Promise<ReportHazardOutput> {
  return reportHazardFlow(input);
}

const reportHazardPrompt = ai.definePrompt({
    name: 'reportHazardPrompt',
    input: {schema: ReportHazardInputSchema},
    output: {schema: ReportHazardOutputSchema},
    prompt: `You are an AI assistant for a smart city traffic management system. A driver has reported a hazard.

Analyze the provided photo and description to understand the nature of the hazard. Your primary role is to acknowledge the report and provide a confirmation.

Description: {{{description}}}
Location: lat: {{{location.lat}}}, lng: {{{location.lng}}}
Photo: {{media url=photoDataUri}}

Generate a unique report ID and a confirmation message for the driver.
Acknowledge the receipt of their report and thank them for helping improve road safety.
Set the status to "Received".
`,
});

const reportHazardFlow = ai.defineFlow(
  {
    name: 'reportHazardFlow',
    inputSchema: ReportHazardInputSchema,
    outputSchema: ReportHazardOutputSchema,
  },
  async input => {
    const {output} = await reportHazardPrompt(input);
    return output!;
  }
);
