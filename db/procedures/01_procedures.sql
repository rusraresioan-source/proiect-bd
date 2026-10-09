-- Procedura: Transfer atomic intre contul curent si contul de economii
CREATE OR REPLACE PROCEDURE transfera_la_economii(
    p_source_id INT,
    p_dest_id INT,
    p_amount NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verificare sold suficient
    IF (SELECT balance FROM accounts WHERE id = p_source_id) < p_amount THEN
        RAISE EXCEPTION 'Fonduri insuficiente pentru transfer';
    END IF;

    -- Debitare cont sursa
    UPDATE accounts 
    SET balance = balance - p_amount 
    WHERE id = p_source_id;

    -- Creditare cont economii
    UPDATE accounts 
    SET balance = balance + p_amount 
    WHERE id = p_dest_id;

    -- Inregistrare tranzactie
    INSERT INTO transactions (
        source_account_id, 
        destination_account_id, 
        type, 
        amount, 
        description
    ) VALUES (
        p_source_id, 
        p_dest_id, 
        'TRANSFER_ECONOMII', 
        p_amount, 
        'Transfer initiat prin procedura stocata'
    );
END;
$$;
