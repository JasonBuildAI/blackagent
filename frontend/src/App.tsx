import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import IntelligenceList from './pages/IntelligenceList';
import IntelligenceDetail from './pages/IntelligenceDetail';
import AnalysisReport from './pages/AnalysisReport';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/intelligence" element={<IntelligenceList />} />
        <Route path="/intelligence/:id" element={<IntelligenceDetail />} />
        <Route path="/analysis/:intelligenceId" element={<AnalysisReport />} />
      </Routes>
    </Layout>
  );
}

export default App;