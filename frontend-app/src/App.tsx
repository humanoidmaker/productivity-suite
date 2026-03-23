import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { EditorLayout } from "./components/layout/EditorLayout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import MyFiles from "./pages/MyFiles";
import DocumentEditor from "./pages/DocumentEditor";
import SpreadsheetEditor from "./pages/SpreadsheetEditor";
import PresentationEditor from "./pages/PresentationEditor";

function Placeholder({ name }: { name: string }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <h1 className="text-xl font-bold text-gray-900">{name}</h1>
        <p className="text-gray-400 text-sm mt-1">Coming in Phase 6</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* Auth pages (no layout) */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Editor pages (minimal chrome) */}
      <Route element={<EditorLayout />}>
        <Route path="/document/:id" element={<DocumentEditor />} />
        <Route path="/spreadsheet/:id" element={<SpreadsheetEditor />} />
        <Route path="/presentation/:id" element={<PresentationEditor />} />
      </Route>

      {/* App pages (sidebar + header) */}
      <Route element={<AppLayout />}>
        <Route index element={<Home />} />
        <Route path="/files" element={<MyFiles />} />
        <Route path="/files/:folderId" element={<MyFiles />} />
        <Route path="/shared" element={<Placeholder name="Shared with Me" />} />
        <Route path="/starred" element={<Placeholder name="Starred" />} />
        <Route path="/trash" element={<Placeholder name="Trash" />} />
        <Route path="/templates" element={<Placeholder name="Templates" />} />
        <Route path="/search" element={<Placeholder name="Search" />} />
        <Route path="/settings" element={<Placeholder name="Settings" />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
