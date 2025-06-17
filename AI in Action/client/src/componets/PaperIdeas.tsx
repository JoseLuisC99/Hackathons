import React, {useEffect} from 'react';
import SearchResult from "../interfaces/SearchResult";
import {
    Accordion, AccordionActions,
    AccordionDetails,
    AccordionSummary,
    Button,
    CircularProgress,
    Container,
    Grid, List, ListItem, ListItemButton, ListItemText, Paper,
    Typography
} from "@mui/material";
import axios from "axios";
import Brainstorm from "../interfaces/Brainstorm";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PostAddIcon from '@mui/icons-material/PostAdd';


function IdeaComponent(idea: {title: string, text: string}) {
    const [references, setReferences] = React.useState<SearchResult[]>([]);
    const [loading, setLoading] = React.useState(false);

    const handleGetReferences = () => {
        setLoading(true)
        axios.post<SearchResult[]>(
            `${process.env.REACT_APP_API_URL}/search`,
            {"search_text": idea.text},
            {headers: {"Content-Type": "application/json"}}
        )
        .then(res => {
            setReferences(res.data)
        })
        .catch(err => alert(err.message))
        .finally(() => setLoading(false))
    }

    return <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography component="span" style={{ fontWeight: "bold" }}>{idea.title}</Typography>
        </AccordionSummary>
        <AccordionDetails>
            <Grid container spacing={2}>
                <Typography>{idea.text}</Typography>
                <List dense>
                    {references.map((item, index) => <ListItem sx={{ width: '100%' }}>
                        <ListItemButton href={`https://arxiv.org/abs/0${item.id}`} target="_blank">
                            <ListItemText primary={item.title} secondary={item.authors} />
                        </ListItemButton>
                    </ListItem>)}
                </List>
            </Grid>
        </AccordionDetails>
        {references.length === 0 && <AccordionActions>
            <Button startIcon={<PostAddIcon />} onClick={handleGetReferences} loading={loading}>Give me some references</Button>
        </AccordionActions>}
    </Accordion>
}

function PaperIdeas(props: {papers: SearchResult[]}) {
    const [brainstorm, setBrainstorm] = React.useState<Brainstorm | null>(null)

    useEffect(() => {
        axios.post<Brainstorm>(
            `${process.env.REACT_APP_API_URL}/brainstorm`,
            {"docs": props.papers},
            {headers: {"Content-Type": "application/json"}}
        )
        .then(res => setBrainstorm(res.data))
        .catch(err => alert(err.message))
    }, [props.papers])

    return <>
        <Container>
            {brainstorm == null && <Grid container justifyContent="center">
                <CircularProgress />
            </Grid>}
            {brainstorm != null && <Grid container spacing={2} padding={2} marginBottom={5}>
                <Typography variant="h4">Your new paper is ready!</Typography>
                <Typography>{brainstorm.synthesis}</Typography>
                <Typography variant="h5">There is some gaps should be cover:</Typography>
                <ul>
                    {brainstorm.gaps.map(gap => <li><Typography>{gap}</Typography></li>)}
                </ul>
                <Typography variant="h5">You can write the next game changing idea in this area:</Typography>
                {brainstorm.ideas.map(idea => <IdeaComponent title={idea.title} text={idea.text} />)}
            </Grid>}
        </Container>
    </>
}

export default PaperIdeas;