import * as fs from 'fs';
import * as path from 'path';
const csvParser = require('csv-parser');

const csvFilePath = path.join(__dirname, '../data/animal_shelter_intake_outcome_mar_2025.csv');

const parseCsvFile = (filePath: string): Promise<any[]> => {
    return new Promise((resolve: any, reject: any) => {
        const results: any[] = [];
        fs.createReadStream(filePath)
            .pipe(csvParser())
            .on('data', (data: any) => results.push(data))
            .on('end', () => resolve(results))
            .on('error', (error: any) => reject(error));
    });
};

(async () => {
    try {
        const data = await parseCsvFile(csvFilePath);
        console.log('Parsed CSV Data:', data);

        // TODO: Transform data
        // TODO: Save data to the database
    } catch (error) {
        console.error('Error reading or parsing the CSV file:', error);
    }
})();
