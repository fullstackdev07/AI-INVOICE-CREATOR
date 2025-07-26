// frontend/src/components/InvoiceEditor.jsx

import React, { useState } from 'react';
import axios from 'axios';

function InvoiceEditor({ initialData }) {
    const [invoice, setInvoice] = useState(initialData);
    const [isExporting, setIsExporting] = useState(false);

    // --- NEW: Handlers for editable items ---

    const handleItemChange = (index, event) => {
        const { name, value } = event.target;
        const newItems = [...invoice.items];
        // Convert quantity and unit_price to numbers
        newItems[index][name] = (name === 'quantity' || name === 'unit_price') ? parseFloat(value) || 0 : value;
        setInvoice(prev => ({ ...prev, items: newItems }));
    };

    const handleAddItem = () => {
        setInvoice(prev => ({
            ...prev,
            items: [...prev.items, { description: '', quantity: 1, unit_price: 0 }]
        }));
    };

    const handleRemoveItem = (index) => {
        const newItems = invoice.items.filter((_, i) => i !== index);
        setInvoice(prev => ({ ...prev, items: newItems }));
    };

    // Generic handler for top-level fields
    const handleChange = (e) => {
        const { name, value } = e.target;
        setInvoice(prev => ({ ...prev, [name]: value }));
    };

    const handleExport = async (format) => {
        setIsExporting(true);
        try {
            const response = await axios.post(
                `http://127.0.0.1:8000/api/export?format=${format}`,
                invoice,
                { responseType: 'blob' }
            );

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            let filename = "invoice";
            if(format === "pdf") filename = `invoice_${invoice.invoice_number}.pdf`;
            if(format === "xml") filename = "invoice.xml";
            if(format === "csv") filename = "invoice_items.csv";
            if(format === "json") filename = "invoice.json";
            
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error(`Error exporting as ${format}:`, error);
            alert(`Failed to export as ${format}. Check the backend console for errors.`);
        }
        setIsExporting(false);
    };

    return (
        <div className="p-8 border rounded-lg shadow-lg bg-white max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-700 border-b pb-4">Edit & Export Invoice</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div>
                    <label className="block text-sm font-medium text-gray-600">Company Name</label>
                    <input type="text" name="company_name" value={invoice.company_name} onChange={handleChange} className="mt-1 p-2 w-full border rounded-md"/>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600">Invoice Title</label>
                    <input type="text" name="title" value={invoice.title} onChange={handleChange} className="mt-1 p-2 w-full border rounded-md"/>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600">Bill To Name</label>
                    <input type="text" name="bill_to_name" value={invoice.bill_to_name} onChange={handleChange} className="mt-1 p-2 w-full border rounded-md"/>
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-600">Invoice Number</label>
                    <input type="text" name="invoice_number" value={invoice.invoice_number} onChange={handleChange} className="mt-1 p-2 w-full border rounded-md"/>
                </div>
            </div>
            
            {/* --- NEW: Fully Editable Items Table --- */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold mb-2">Items</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-gray-100">
                                <th className="p-2 w-1/2">Description</th>
                                <th className="p-2">Qty</th>
                                <th className="p-2">Unit Price</th>
                                <th className="p-2">Total</th>
                                <th className="p-2"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoice.items.map((item, index) => (
                                <tr key={index} className="border-b">
                                    <td className="p-1"><input type="text" name="description" value={item.description} onChange={(e) => handleItemChange(index, e)} className="p-1 w-full border rounded-md"/></td>
                                    <td className="p-1"><input type="number" name="quantity" value={item.quantity} onChange={(e) => handleItemChange(index, e)} className="p-1 w-20 border rounded-md"/></td>
                                    <td className="p-1"><input type="number" name="unit_price" value={item.unit_price} onChange={(e) => handleItemChange(index, e)} className="p-1 w-24 border rounded-md"/></td>
                                    <td className="p-1">${(item.quantity * item.unit_price).toFixed(2)}</td>
                                    <td className="p-1"><button onClick={() => handleRemoveItem(index)} className="text-red-500 hover:text-red-700 font-bold">X</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <button onClick={handleAddItem} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
                    + Add Item
                </button>
            </div>

            <div className="flex flex-wrap gap-4 justify-center pt-6 border-t">
                 <button onClick={() => handleExport('pdf')} disabled={isExporting} className="bg-red-500 text-white px-5 py-2 rounded-md hover:bg-red-600 disabled:bg-gray-400">Export PDF</button>
                 <button onClick={() => handleExport('xml')} disabled={isExporting} className="bg-orange-500 text-white px-5 py-2 rounded-md hover:bg-orange-600 disabled:bg-gray-400">Export XML</button>
                 <button onClick={() => handleExport('csv')} disabled={isExporting} className="bg-green-500 text-white px-5 py-2 rounded-md hover:bg-green-600 disabled:bg-gray-400">Export CSV</button>
                 <button onClick={() => handleExport('json')} disabled={isExporting} className="bg-gray-600 text-white px-5 py-2 rounded-md hover:bg-gray-700 disabled:bg-gray-400">Export JSON</button>
            </div>
        </div>
    );
}

export default InvoiceEditor;