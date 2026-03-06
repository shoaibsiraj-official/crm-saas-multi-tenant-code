'use client';

import Link from "next/link";
import { useEffect, useState } from "react";
import axios from "@/lib/axios";
import Card from "@/app/components/ui/Card";
import Badge from "@/app/components/ui/Badge";
import Button from "@/app/components/ui/Button";
import { Plus } from "lucide-react";

export default function InvoicesPage() {

const [invoices, setInvoices] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetchInvoices();
}, []);

// Fetch invoices
const fetchInvoices = async () => {
  try {

    const res = await axios.get("/invoices/");
    console.log("INVOICE API:", res.data);

    let invoiceArray = [];

    if (Array.isArray(res.data)) {
      invoiceArray = res.data;
    } else if (Array.isArray(res.data?.results)) {
      invoiceArray = res.data.results;
    } else if (Array.isArray(res.data?.data?.results)) {
      invoiceArray = res.data.data.results;
    }

    setInvoices(invoiceArray);

  } catch (error) {

    console.error("Invoice API error:", error);
    setInvoices([]);

  } finally {

    setLoading(false);

  }
};

// Stats
const stats = Array.isArray(invoices)
  ? invoices.reduce(
      (acc, inv) => {

        const amount = Number(inv.total || inv.amount || 0);

        if (inv.status === "PAID") acc.paid += amount;
        if (inv.status === "SENT" || inv.status === "DRAFT") acc.pending += amount;
        if (inv.status === "OVERDUE") acc.overdue += amount;

        return acc;

      },
      { paid: 0, pending: 0, overdue: 0 }
    )
  : { paid: 0, pending: 0, overdue: 0 };

const formatCurrency = (amount) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
  }).format(Number(amount || 0));

const formatDate = (date) =>
  date ? new Date(date).toLocaleDateString() : "-";

const getStatusVariant = (status) => {
  switch (status) {
    case "PAID":
      return "success";
    case "SENT":
      return "warning";
    case "OVERDUE":
      return "danger";
    case "DRAFT":
      return "default";
    default:
      return "default";
  }
};

return (
<div className="space-y-6">

  {/* Header */}
  <div className="flex justify-between items-center">
    <h1 className="text-2xl font-bold">Invoices</h1>

    <Link href="/organization/invoices/create">
      <Button>
        <Plus className="w-4 h-4 mr-2" />
        Create Invoice
      </Button>
    </Link>
  </div>

  {/* Summary */}
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

    <Card className="p-4">
      <h3 className="text-gray-500 text-sm">Paid</h3>
      <p className="text-xl font-bold text-green-600">
        {formatCurrency(stats.paid)}
      </p>
    </Card>

    <Card className="p-4">
      <h3 className="text-gray-500 text-sm">Pending</h3>
      <p className="text-xl font-bold text-yellow-600">
        {formatCurrency(stats.pending)}
      </p>
    </Card>

    <Card className="p-4">
      <h3 className="text-gray-500 text-sm">Overdue</h3>
      <p className="text-xl font-bold text-red-600">
        {formatCurrency(stats.overdue)}
      </p>
    </Card>

  </div>

  {/* Table */}
  <Card className="overflow-hidden">

    {loading ? (

      <div className="p-6 text-center">
        Loading invoices...
      </div>

    ) : (

      <table className="w-full text-sm">

        <thead className="bg-gray-50">
          <tr>
            <th className="p-3 text-left">Invoice #</th>
            <th className="p-3 text-left">Client</th>
            <th className="p-3 text-left">Amount</th>
            <th className="p-3 text-left">Status</th>
            <th className="p-3 text-left">Due Date</th>
          </tr>
        </thead>

        <tbody>

          {Array.isArray(invoices) && invoices.length > 0 ? (

            invoices.map((inv) => (

              <tr key={inv.id} className="border-t">

                <td className="p-3">{inv.invoice_number}</td>

                <td className="p-3">{inv.client_name}</td>

                <td className="p-3">
                  {formatCurrency(inv.total || inv.amount)}
                </td>

                <td className="p-3">
                  <Badge variant={getStatusVariant(inv.status)}>
                    {inv.status}
                  </Badge>
                </td>

                <td className="p-3">
                  {formatDate(inv.due_date)}
                </td>

              </tr>

            ))

          ) : (

            <tr>
              <td colSpan="5" className="text-center py-6">
                No invoices found
              </td>
            </tr>

          )}

        </tbody>

      </table>

    )}

  </Card>

</div>
);
}