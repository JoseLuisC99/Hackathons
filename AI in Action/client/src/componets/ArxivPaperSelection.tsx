import React from 'react';
import SearchResult from "../interfaces/SearchResult";
import {
    Button,
    Card,
    CardActions,
    CardContent,
    CardHeader,
    Container, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Fab,
    Grid,
    IconButton, Snackbar, Tooltip,
    Typography
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import ThumbUpOffAltIcon from '@mui/icons-material/ThumbUpOffAlt';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import HistoryEduIcon from '@mui/icons-material/HistoryEdu';
import axios from "axios";


function MoreLikeThisButton(props: {paper: SearchResult, onSuccess: Function, onError: Function}) {
    const [disabled, setDisabled] = React.useState(false);
    const [loading, setLoading] = React.useState(false);

    const handleClick = () => {
        setLoading(true)
        axios.post<SearchResult[]>(
            `${process.env.REACT_APP_API_URL}/vectorSearch`,
            {"embedding": props.paper.embedding},
            {headers: {"Content-Type": "application/json"}}
        )
        .then((res) => {
            props.onSuccess(res.data)
            setDisabled(true)
        })
        .catch((err) => props.onError(err.message))
        .finally(() => setLoading(false))
    }

    return <Button
        size="small"
        color="secondary"
        startIcon={<ThumbUpOffAltIcon />}
        onClick={handleClick}
        disabled={disabled}
        loading={loading}
    >
        More like this
    </Button>
}


function ArxivPaperSelection(props: {papers: SearchResult[], query: string, callback: Function}) {
    const [paperList, setPaperList] = React.useState<SearchResult[]>(props.papers);
    const [openSnackbar, setOpenSnackbar] = React.useState(false);
    const [snackbarMessage, setSnackbarMessage] = React.useState("");
    const [openDialog, setOpenDialog] = React.useState(false);
    const [dialogContent, setDialogContent] = React.useState("");
    const [loadingRelevance, setLoadingRelevance] = React.useState(false);

    const onSuccess = (result: SearchResult[]) => {
        let papersToAdd = []
        for (let newPaper of result) {
            if (paperList.find(p => p.id === newPaper.id)) continue
            newPaper.search_score = NaN
            papersToAdd.push(newPaper)
        }
        setPaperList([...paperList, ...papersToAdd])
        setSnackbarMessage(`${papersToAdd.length} new papers added successfully.`)
        setOpenSnackbar(true);
    }
    const onError = (error: string) => {
        setSnackbarMessage(error)
        setOpenSnackbar(true);
    }

    const handleDeletePaper = (paperToDelete: SearchResult) => {
        setPaperList(paperList.filter(item => item !== paperToDelete))
        setSnackbarMessage(`Article '${paperToDelete.title.slice(0, 30)}...' was deleted successfully.`)
        setOpenSnackbar(true);
    }

    const handleOpenSnackbar = () => {
        setOpenSnackbar(false);
    }

    const handleRelevance = (query: string, abstract: string) => {
        setLoadingRelevance(true)
        axios.post<string>(
            `${process.env.REACT_APP_API_URL}/relevance`,
            {query: query, abstract: abstract},
            {headers: {"Content-Type": "application/json"}}
        )
        .then((res) => {
            setOpenDialog(true)
            setDialogContent(res.data)
        })
        .catch((err) => alert(err.message))
        .finally(() => setLoadingRelevance(false))
}

    return <>
        <Container>
            <Grid container spacing={2} padding={3}>
                {/* eslint-disable-next-line array-callback-return */}
                {paperList.map((paper, i) => (
                    <Grid size={12}>
                        <Card variant="outlined">
                            <CardHeader
                                title={paper.title}
                                subheader={Number.isNaN(paper.search_score) ?  "" : `Score of relevance: ${paper.search_score.toFixed(3)}`}
                                action={
                                    <Tooltip title="Why is this paper relevant?">
                                        <IconButton
                                            size="small"
                                            onClick={() => handleRelevance(props.query, paper.abstract)}
                                            loading={loadingRelevance}
                                        >
                                            <HelpOutlineIcon />
                                        </IconButton>
                                    </Tooltip>
                                }
                            />
                            <CardContent>
                                <Typography variant="body2" sx={{ color: 'text.secondary' }}>{paper.abstract}</Typography>
                            </CardContent>
                            <CardActions sx={{ justifyContent: 'flex-end' }}>
                                <Button
                                    size="small"
                                    color="error"
                                    startIcon={<DeleteIcon />}
                                    onClick={() => handleDeletePaper(paper)}
                                >
                                    Not use it
                                </Button>
                                <MoreLikeThisButton paper={paper} onSuccess={onSuccess} onError={onError} />
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
        <Snackbar
            open={openSnackbar}
            autoHideDuration={5000}
            onClose={handleOpenSnackbar}
            message={snackbarMessage}
        />
        <Dialog open={openDialog}>
            <DialogTitle>Why does this paper can help you?</DialogTitle>
            <DialogContent>
                <DialogContentText>{dialogContent}</DialogContentText>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)} color="secondary">Close</Button>
                </DialogActions>
            </DialogContent>
        </Dialog>
        <Fab
            variant="extended"
            color="primary"
            style={{margin: 0, top: 'auto', right: "2rem", bottom: "2rem", left: 'auto', position: 'fixed'}}
            onClick={() => props.callback(paperList)}
        >
            <HistoryEduIcon sx={{ mr: 1 }} />
            Continue
        </Fab>
    </>
}

export default ArxivPaperSelection;