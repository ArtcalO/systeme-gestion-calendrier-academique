import {useGenAi} from './useGenAi.js'

export const useGetGenerativeModelGP = async (prompt) => {

    const model = await useGenAi('gemini-pro');
    const result = await model.generateContent(`Suggest 10 meals I can cook with these ingredients: ${prompt}. Provide the response as a list of meal names.`);
    const response = await result.response;
    const text = response.text();

    return text.split('\n').filter(line => line.trim());;
}