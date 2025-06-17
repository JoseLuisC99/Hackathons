import React, {Fragment} from 'react';
import {Box, Container, Step, StepButton, Stepper, Typography} from "@mui/material";
import SearchInput from "./componets/SearchInput";
import SearchResult from "./interfaces/SearchResult";
import ArxivPaperSelection from "./componets/ArxivPaperSelection";
import PaperIdeas from "./componets/PaperIdeas";

const arxiv_steps = ["Query prompt", "Select your papers", "Your next paper!"]

function App() {
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState<{[k: number]: boolean}>({});
  const [query, setQuery] = React.useState("");
  const [searchData, setSearchData] = React.useState<SearchResult[]>([]);
  const [papers, setPapers] = React.useState<SearchResult[]>([]);

  const totalSteps = () => {
    return arxiv_steps.length;
  };

  const completedSteps = () => {
    return Object.keys(completed).length;
  };

  const isLastStep = () => {
    return activeStep === totalSteps() - 1;
  };

  const allStepsCompleted = () => {
    return completedSteps() === totalSteps();
  };

  const handleNext = () => {
    const newActiveStep =
        isLastStep() && !allStepsCompleted()?
            arxiv_steps.findIndex((step, i) => !(i in completed))
            : activeStep + 1;
    setActiveStep(newActiveStep);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStep = (step: number) => () => {
    setActiveStep(step);
  };

  const handleComplete = () => {
    setCompleted({
      ...completed,
      [activeStep]: true,
    });
    handleNext();
  };

  const handleReset = () => {
    setActiveStep(0);
    setCompleted({});
  };

  const handleQueryData = (papers: SearchResult[], query: string) => {
    setQuery(query);
    setSearchData(papers);
    handleComplete()
  }

  const handlePaperSelected = (papers: SearchResult[]) => {
    setPapers(papers);
    handleComplete()
  }

  return <Box sx={{ width: "100%" }} style={{marginTop: "2rem"}}>
    <Container style={{ marginBottom: "3rem" }}>
      <Typography variant="h1" component="div" align="center">Paper Pal AI</Typography>
      <Typography variant="h6" align="center">Academic Paper Recommender & Summarizer</Typography>
      <Typography variant="body1" component="div" align="justify" style={{ padding: "3rem" }}>
        Leveraging AI to semantically search, summarize, and recommend academic papers. Navigating the vast world of
        academic papers can be overwhelming. Paper Pal AI is your intelligent research companion, leveraging cutting-edge AI
        and powerful cloud technology to transform how you discover, understand, and interact with academic literature.
      </Typography>

      <Stepper nonLinear activeStep={activeStep}>
        {arxiv_steps.map((label, index) => (
            <Step key={label} completed={completed[index]}>
              <StepButton color="inherit" onClick={handleStep(index)} disabled>
                {label}
              </StepButton>
            </Step>
        ))}
      </Stepper>
    </Container>
    <Fragment>
      {activeStep === 0 && <SearchInput onSuccess={handleQueryData} onError={() => handleReset()} />}
      {activeStep === 1 && <ArxivPaperSelection papers={searchData} query={query} callback={handlePaperSelected} />}
      {activeStep === 2 && <PaperIdeas papers={papers} />}
    </Fragment>

  </Box>;
}

export default App;
