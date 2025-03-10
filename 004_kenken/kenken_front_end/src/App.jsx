import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "tailwindcss/tailwind.css";

export default function KenKenGame() {
    const [size, setSize] = useState(6);
    const [puzzle, setPuzzle] = useState(null);
    const [userGrid, setUserGrid] = useState([]);

    useEffect(() => {
        fetchPuzzle(size);
    }, [size]);

    const fetchPuzzle = async (size) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/generate?size=${size}`);
            if (!response.ok) {
                throw new Error("Failed to fetch puzzle");
            }
            const data = await response.json();
            setPuzzle(data);
            setUserGrid(Array.from({ length: size }, () => Array(size).fill("")));
        } catch (error) {
            console.error("Error fetching puzzle:", error);
        }
    };

    const handleInputChange = (row, col, value) => {
        const newGrid = [...userGrid];
        newGrid[row][col] = value;
        setUserGrid(newGrid);
    };

    return (
        <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold mb-6">KenKen Puzzle</h1>
            <div className="mb-4">
                <label className="mr-2 text-lg font-medium">Grid Size:</label>
                <select 
                    value={size} 
                    onChange={(e) => setSize(parseInt(e.target.value))} 
                    className="border p-2 rounded shadow-md bg-white">
                    {[6, 7, 8, 9].map((s) => (
                        <option key={s} value={s}>{s}x{s}</option>
                    ))}
                </select>
            </div>
            <button onClick={() => fetchPuzzle(size)} 
                className="px-4 py-2 bg-blue-500 text-white rounded mb-6 shadow-md hover:bg-blue-700">
                Generate Puzzle
            </button>
            {puzzle && (
                <motion.div 
                    className="grid gap-1 border-4 border-gray-800 p-4 bg-white rounded-lg shadow-lg"
                    style={{ gridTemplateColumns: `repeat(${size}, 1fr)`, width: "fit-content" }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}>
                    {puzzle.grid.map((row, rowIndex) =>
                        row.map((cell, colIndex) => (
                            <div 
                                key={`${rowIndex}-${colIndex}`} 
                                className="relative flex justify-center items-center h-16 w-16 border border-gray-700 text-xl font-bold bg-gray-50">
                                <input 
                                    type="text" 
                                    value={userGrid[rowIndex][colIndex]} 
                                    onChange={(e) => handleInputChange(rowIndex, colIndex, e.target.value)}
                                    className="w-full h-full text-center bg-transparent border-none outline-none text-gray-900 font-bold text-lg"
                                />
                                {puzzle.cages.some(cage => cage.cells.some(([r, c]) => r === rowIndex && c === colIndex)) && (
                                    <div className="absolute top-1 left-1 text-xs text-gray-500">
                                        {puzzle.cages.find(cage => cage.cells.some(([r, c]) => r === rowIndex && c === colIndex))?.target}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </motion.div>
            )}
        </div>
    );
}
