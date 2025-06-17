import React from 'react';
import {
    Button, Container,
    FormControl, Grid,
    InputLabel,
    OutlinedInput,
} from "@mui/material";
import axios from "axios";
import SearchResult from "../interfaces/SearchResult";

function SearchInput(props: {onSuccess: Function, onError: Function}) {
    const [searchQuery, setSearchQuery] = React.useState("Quantum mechanics analysis using algebraic graph theory")
    const [loading, setLoading] = React.useState(false);

    const searchClick = () => {
        setLoading(true)
        axios.post<SearchResult[]>(
            `${process.env.REACT_APP_API_URL}/search`,
            {"search_text": searchQuery},
            {headers: {"Content-Type": "application/json"}}
        )
        .then((res) => props.onSuccess(res.data, searchQuery))
        .catch((err) => props.onError(err))
        .finally(() => setLoading(false));
    };
    return <Container>
        <Grid container spacing={2}>
            <Grid size={8} offset={{xs: 2}}>
                <FormControl fullWidth>
                    <InputLabel htmlFor="search-query">What do you want to write your next article about?</InputLabel>
                    <OutlinedInput
                        id="search-query"
                        multiline
                        rows={4}
                        label="What do you want to write your next article about?"
                        value={searchQuery}
                        disabled={loading}
                        onChange={(e) => {setSearchQuery(e.target.value)}}
                    />
                    {/*<FormHelperText>I want to write a paper about...</FormHelperText>*/}
                </FormControl>
            </Grid>
            {/*Button section*/}
            <Grid size={8} offset={{xs: 2}} container justifyContent="flex-end">
                <Button
                    variant="outlined"
                    component="div"
                    onClick={searchClick}
                    loading={loading}
                >
                    Go ahead!
                </Button>
            </Grid>
        </Grid>
    </Container>
}

export default SearchInput;
