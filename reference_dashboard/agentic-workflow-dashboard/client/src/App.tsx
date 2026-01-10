import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Workflows from "./pages/Workflows";
import Errors from "./pages/Errors";
import Monitor from "./pages/Monitor";
import Settings from "./pages/Settings";
import WorkflowEditor from "./pages/WorkflowEditor";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/workflows" component={Workflows} />
      <Route path="/workflow/:id" component={WorkflowEditor} />
      <Route path="/errors" component={Errors} />
      <Route path="/monitor" component={Monitor} />
      <Route path="/settings" component={Settings} />
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
