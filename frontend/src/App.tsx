import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import IntelligenceList from './pages/IntelligenceList';
import IntelligenceDetail from './pages/IntelligenceDetail';
import AnalysisReport from './pages/AnalysisReport';
import Settings from './pages/Settings';
import DataSourcePage from './pages/DataSourcePage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/intelligence" element={<IntelligenceList />} />
        <Route path="/intelligence/:id" element={<IntelligenceDetail />} />
        <Route path="/analysis/:intelligenceId" element={<AnalysisReport />} />
        <Route path="/sources" element={<DataSourcePage />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;