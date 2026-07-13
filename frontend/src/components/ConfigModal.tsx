import { useState, useEffect } from "react";
import { 
    Modal, 
    Box,
    Button,
    MenuItem, 
    TextField, 
    FormControl, 
    InputLabel, 
    Select, 
    Typography,
    Switch,
    FormControlLabel
} from "@mui/material";
import { type Config, type PolicyTypes, PolicyTypeArray } from "../api/types";
import './ConfigModal.css'


interface Props {
    open: boolean,
    handleClose: () => void
    setRunConfig: (config: Config) => void
}

const generateRandom32Bit = (): number => {
    const array = new Uint32Array(1);;
    crypto.getRandomValues(array);
    return array[0];
}

const initSeed = generateRandom32Bit()

const ConfigModal = ({open, handleClose, setRunConfig}: Props) => {
    const [policyType, setPolicyType] = useState<PolicyTypes | undefined>(undefined);
    const [serverCount, setServerCount] = useState<number | undefined>(undefined);
    const [maxQueueLength, setMaxQueueLength] = useState<number | undefined>(undefined);
    const [serverLoad, setServerLoad] = useState<number | undefined>(undefined);
    const [seed, setSeed] = useState<number | undefined>(initSeed);
    const [maxRequests, setMaxRequests] = useState<number | undefined>(undefined);
    const [warmup, setWarmup] = useState<number | undefined>(undefined);
    const [failuresEnabled, setFailuresEnabled] = useState<boolean>(false);
    const [mtbf, setMtbf] = useState<number | null>(2000);
    const [mttr, setMttr] = useState<number | null>(50);
    const [buttonEnabled, setButtonEnabled] = useState<boolean>(false);

    const [serverCountValid, setServerCountValid] = useState<boolean>(true);
    const [queueLenValid, setQueueLenValid] = useState<boolean>(true);
    const [maxRequestsValid, setMaxRequestsValid] = useState<boolean>(true);
    const [warmuptValid, setWarmupValid] = useState<boolean>(true);
    const [mtbfValid, setMtbfCountValid] = useState<boolean>(true);
    const [mttrValid, setMttrCountValid] = useState<boolean>(true);

    const wholeNumberRegx =/^\d*$/;

    const handleSetRunConfig = () => {
        const config: Config = {
            policy: policyType,
            c: serverCount,
            k: maxQueueLength,
            rho: serverLoad,
            seed: seed,
            max_requests: maxRequests,
            warmup: warmup,
            failures_enabled: failuresEnabled,
            MTBF: mtbf,
            MTTR: mttr
        }
        setRunConfig(config);
        handleClose();
    }

    const hangleChange = (event) => {
        const { id, value } = event.target;

        switch (id) {
            case "ServerCount":
                setServerCountValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setServerCount(parseInt(value));
                break;

            case "QueueLength":
                setQueueLenValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setMaxQueueLength(parseInt(value));
                break;

            case "MaxRequests":
                setMaxRequestsValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setMaxRequests(parseInt(value));
                break;

            case "Warmup":
                setWarmupValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setWarmup(parseInt(value));
                break;

            case "MTBF":
                setMtbfCountValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setMtbf(parseInt(value));
                break;

            case "MTTR":
                setMttrCountValid(wholeNumberRegx.test(value) && parseInt(value) > 0);
                setMttr(parseInt(value));
                break;
        }

    }

    const showFailureConfigs = () => {
        if (failuresEnabled) {
            return (
            <>
                <TextField
                    className="config-field"
                    id="MTBF"
                    label="MTBF"
                    required
                    type="number"
                    error={!mtbfValid}
                    defaultValue={mtbf}
                    onChange={hangleChange}
                />
                <TextField
                    className="config-field"
                    id="MTTR"
                    label="MTTR"
                    required
                    type="number"
                    error={!mttrValid}
                    defaultValue={mttr}
                    onChange={hangleChange}
                />
            </>
        );
        }
    }

    useEffect(() => {
        const buttonStatus = (() => {
            setButtonEnabled(
                policyType != undefined
                && serverCount != undefined
                && maxQueueLength != undefined
                && serverLoad != undefined
                && seed != undefined
                && maxRequests != undefined
                && warmup != undefined
            )
        })

        return () => buttonStatus()
    }, [policyType, serverCount, maxQueueLength, serverLoad, seed, maxRequests, warmup])

    return (
        <Modal
            className="modal-container"
            open={open}
            onClose={handleClose}
        >
            <div className="modal-box-container">
                <Typography 
                    className="config-params-label" 
                    variant="h5" 
                >
                    Simulator Configuration
                </Typography>
                <Box className="config-form-container">
                    <FormControl fullWidth>
                        <InputLabel id="policy-type">Policy-Type</InputLabel>
                        <Select
                            className="policy-type"
                            labelId="policy-type"
                            required
                            defaultValue={policyType}
                            onChange={(e) => setPolicyType(e.target.value as PolicyTypes)}
                        >
                            {
                                PolicyTypeArray.map((type) => {
                                    return (
                                        <MenuItem value={type}>{type}</MenuItem>
                                    )
                                })
                            }
                        </Select>
                    </FormControl>
                    <TextField
                        className="config-field"
                        id="ServerCount"
                        label="Number of Servers"
                        variant="outlined"
                        required
                        type="number"
                        error={!serverCountValid}
                        defaultValue={serverCount}
                        onChange={hangleChange}
                    />
                    <TextField
                        className="config-field"
                        id="QueueLength"
                        label="Max Queue Length"
                        required
                        type="number"
                        error={!queueLenValid}
                        defaultValue={maxQueueLength}
                        onChange={hangleChange}
                    />
                    <TextField
                        className="config-field"
                        label="Server Load (max 1)"
                        required
                        error={serverLoad < 0 || serverLoad >= 1}
                        type="number"
                        onChange={(e) => setServerLoad(parseFloat(e.target.value))}
                    />
                    <TextField
                        className="config-field"
                        label="Seed"
                        type="number"
                        defaultValue={seed}
                        required
                        onChange={(e) => setSeed(parseInt(e.target.value))}
                    />
                    <TextField
                        className="config-field"
                        id="MaxRequests"
                        label="Number of Requests"
                        required
                        type="number"
                        error={!maxRequestsValid}
                        defaultValue={maxRequests}
                        onChange={hangleChange}
                    />
                    <TextField
                        className="config-field"
                        id="Warmup"
                        label="Warmup Requests"
                        required
                        type="number"
                        error={!warmuptValid}
                        defaultValue={warmup}
                        onChange={hangleChange}
                    />
                    <FormControlLabel 
                        className="enale-failures-switch"
                        label="Enable Failures"
                        control=
                        {
                            <Switch 
                                sx={{ marginLeft: "18px"}}
                                checked={failuresEnabled} 
                                onChange={() => setFailuresEnabled(!failuresEnabled)}
                            />
                        } 
                    />
                    {
                        showFailureConfigs()
                    }
                </Box>
                <Button
                    onClick={() => handleSetRunConfig()}
                    disabled={!buttonEnabled}
                >
                    Set
                </Button>
            </div>
        </Modal>
    );
}

export default ConfigModal;